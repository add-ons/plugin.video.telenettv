from resources.lib.Authentication import Authentication
from resources.lib.Classes.Devices import Device
from resources.lib.Utils import Utils
from resources.lib.Classes.Channel import Channel
from resources.lib.Classes.Stream import Stream
from resources.lib.Utils.PluginCache import PluginCache
from resources.lib.Classes.StreamingFormat import StreamingFormat
import random
import json
import base64
from datetime import datetime, timedelta
import time

from resources.lib.kodiwrapper import KodiWrapper


DEVICE_NAME = "Mijn computer - Google Chrome"
DEVICE_CLASS = "other"
TOKEN_EXPIRY_GAP_MINUTES = 30

if not PluginCache.key_exists("deviceId"):
    PluginCache.set_data({"deviceId": "fe88cd8ace897d72c78441f648a2f92a4e298cced867179932d7c2751d79fb83"})


class BadRequest(object):
    class KnownErrorCodes:
        DEVICE_UNREGISTERED = "deviceUnregistered"
        DEVICE_UNREGISTERED_DEVICE_LIMIT_REACHED = "deviceUnregisteredDeviceLimitReached"

    def __init__(self, error_type="", code="", reason=""):
        self.type = error_type
        self.code = code
        self.reason = reason

    @staticmethod
    def parse_error_object(json_data):
        error_obj = json_data[0]

        try:
            return BadRequest(
                error_type=error_obj.get("type"),
                code=error_obj.get("code"),
                reason=error_obj.get("reason")
            )
        except KeyError:
            return BadRequest()


class TelenetTV(Authentication):
    def __init__(self, session, logger_instance=None):
        super(self.__class__, self).__init__(session)
        self.logger = logger_instance

        self.device_id = PluginCache.get_by_key("deviceId")
        self.oesp_token = PluginCache.get_by_key("oespToken")
        self.shared_profile_id = PluginCache.get_by_key("sharedProfileId")
        self.license_token = ""

        if self.must_login():
            self.web_authorization()
            self.authorize()
            self.login()
            self.request_tokens()

        self._check_oesp_validity()

    def construct_header(self, content_type='application/json'):
        header = {
            'User-Agent': self.USER_AGENT,
            'Accept': content_type,
            'Content-Type': content_type,
            'X-OESP-Token': self.oesp_token,
            'X-OESP-Username': self.username,
            'X-OESP-Profile-Id': self.shared_profile_id,
            'X-Client-Id': self.CLIENT_ID
        }

        return header

    @staticmethod
    def must_login():
        return not PluginCache.key_exists("oespToken") or not PluginCache.key_exists("token")

    def refresh_token(self):
        r = Utils.make_request(self.session,
                               method="GET",
                               url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/session",
                               headers=self.construct_header())

        json_data = r.json()

        oesp_token = json_data["oespToken"]
        PluginCache.set_data({
            "oespToken": oesp_token
        })


    def get_program_schedule(self, station_id):
        timestamp = int(time.time())

        r = Utils.make_request(self.session,
                               method="GET",
                               url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/listings?"
                                   "byEndTime={}~"
                                   "&byStationId={}"
                                   "&range=1-1&sort=startTime".format(timestamp, station_id),
                               headers={'User-Agent': self.USER_AGENT})

        json_data = r.json()
        program = json_data["listings"][0]["program"]

        return program

    def get_channels(self):
        r = Utils.make_request(
            self.session,
            method="GET",
            headers=self.construct_header(),
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/channels?"
                "includeInvisible=false"
                "&sort=channelNumber")

        json_data = r.json()

        useful_channel_data = []
        entitlements = PluginCache.get_by_key("entitlements")

        if not entitlements:
            return useful_channel_data

        if "channels" in json_data:
            fetched_channel_data = json_data["channels"]
            for channel_data in fetched_channel_data:
                station = channel_data["stationSchedules"][0]["station"]
                video_streams = station["videoStreams"]

                if video_streams:
                    channel = Channel(channel_data["id"],
                                      station["id"],
                                      channel_data["title"],
                                      channel_data["channelNumber"],
                                      bool(station["hasLiveStream"]),
                                      station["entitlements"])

                    if not any(x in entitlements for x in channel.entitlements):
                        continue

                    HLS_stream = {}
                    DASH_stream = {}
                    HSS_stream = {}

                    for video_stream in video_streams:
                        if "Orion-HLS" in video_stream["assetTypes"]:
                            HLS_stream = Stream(
                                video_stream["streamingUrl"],
                                video_stream["contentLocator"],
                                video_stream["protectionKey"])

                        if "Orion-DASH" in video_stream["assetTypes"]:
                            DASH_stream = Stream(
                                video_stream["streamingUrl"],
                                video_stream["contentLocator"],
                                video_stream["protectionKey"])

                        if "Orion-HSS" in video_stream["assetTypes"]:
                            HSS_stream = Stream(
                                video_stream["streamingUrl"],
                                video_stream["contentLocator"],
                                video_stream["protectionKey"])

                    thumbnail = [img["url"] for img in station["images"]
                                 if img["assetType"] == "station-logo-xlarge"][0]

                    imageStream = [img["url"] for img in station["images"]
                                   if img["assetType"] == "imageStream"][0]

                    channel.thumbnail = thumbnail
                    channel.stream_thumbnail = imageStream
                    channel.stream_DASH = DASH_stream
                    channel.stream_HLS = HLS_stream
                    channel.stream_HSS = HSS_stream

                    useful_channel_data.append(channel)

        return useful_channel_data

    def request_tokens(self):
        self._get_refresh_token()
        self._get_oesp_token()

    def clear_streams(self):
        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/playback/clearstreams",
            headers=self.construct_header())

    def _check_registered_devices(self):
        r = Utils.make_request(
            self.session,
            method="GET",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/devices/status",
            headers=self.construct_header())

        json_data = r.json()

        return json_data

    def get_registered_device_list(self):
        json_data = self._check_registered_devices()
        return Device.get_list(json_data)

    def registered_device_limit_reached(self):
        json_data = self._check_registered_devices()

        current_registered = int(json_data["currentRegisteredDevices"])
        max_registered = int(json_data["maxRegisteredDevices"])

        return current_registered >= max_registered

    def replace_registered_device(self, old_device_id, new_device_id):
        json_payload = {
            "deviceId": new_device_id,
            "deviceName": DEVICE_NAME,
            "customerDefinedName": DEVICE_NAME,
            "deviceClass": DEVICE_CLASS
        }

        r = Utils.make_request(
            self.session,
            method="PUT",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/devices/{}".format(old_device_id),
            headers=self.construct_header(),
            data=json_payload)

        json_data = r.json()

        return json_data["deviceId"]

    def _request_license_token(self, content_locator):
        json_payload = {
            "contentLocator": content_locator
        }

        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/license/token",
            headers=self.construct_header(),
            data=json_payload)

        try:
            json_data = r.json()
        except ValueError:
            json_data = ""

        return r.status_code, json_data

    def request_license_token(self, content_locator):
        # retry once
        for _ in range(2):
            status_code, json_data = self._request_license_token(content_locator)

            if status_code == 200:
                license_token = json_data.get("token")

                PluginCache.set_data({
                    "licenseToken": license_token
                })

                break
            elif status_code == 400:
                new_device_id = Utils.create_token(64)
                bad_request = BadRequest.parse_error_object(json_data)

                if bad_request.code == BadRequest.KnownErrorCodes.DEVICE_UNREGISTERED:
                    self._register_device(new_device_id)
                    PluginCache.set_data({"deviceId": new_device_id})
                elif bad_request.code == BadRequest.KnownErrorCodes.DEVICE_UNREGISTERED_DEVICE_LIMIT_REACHED:
                    # get the existing registered devices
                    existing_devices = self.get_registered_device_list()

                    # select a random device to swap
                    random_device = random.choice(existing_devices)

                    # replace registered device with the randomly selected one
                    self.replace_registered_device(random_device.device_id, new_device_id)
                    PluginCache.set_data({"deviceId": new_device_id})

    def create_manifest_url(self, base_uri, channel):
        self.license_token = PluginCache.get_by_key("licenseToken")

        streaming_format = StreamingFormat.get_streaming_format()
        if streaming_format == StreamingFormat.MPEG_DASH:
            url = Stream.BASE_URL_MPD
        elif streaming_format == StreamingFormat.SMOOTH_STREAM:
            url = Stream.BASE_URL_HSS
        else:
            url = ""

        formatted_url = url.format(base_uri, channel, self.license_token)

        return formatted_url

    def _get_refresh_token(self):
        token = PluginCache.get_by_key("token")
        validity_token = PluginCache.get_by_key("validityToken")
        state = PluginCache.get_by_key("state")

        json_payload = {
            "authorizationGrant":
                {
                    "authorizationCode": token,
                    "validityToken": validity_token,
                    "state": state
                }
        }

        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/authorization",
            headers=self.construct_header(),
            data=json_payload)

        json_data = r.json()

        refresh_token = json_data["refreshToken"]

        PluginCache.set_data({
            "refreshToken": refresh_token,
        })

    def _get_oesp_token(self):
        refresh_token = PluginCache.get_by_key("refreshToken")

        json_payload = {
            "refreshToken": refresh_token,
            "username": self.username
        }

        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/session?token=true",
            headers=self.construct_header(),
            data=json_payload)

        json_data = r.json()

        oesp_token = json_data["oespToken"]
        shared_profile_id = json_data["customer"]["sharedProfileId"]
        entitlements = json_data["entitlements"]

        PluginCache.set_data({
            "oespToken": oesp_token,
            "sharedProfileId": shared_profile_id,
            "entitlements": entitlements
        })

    def _check_oesp_validity(self):
        if self.oesp_token:
            oesp_token_split = self.oesp_token.split(".")
            middle_oesp_part = base64.b64decode(oesp_token_split[1] + 2 * "=")

            json_data = json.loads(middle_oesp_part)
            expiry_timestamp = json_data.get("exp")

            now = datetime.utcnow()
            expiry_date = datetime.fromtimestamp(expiry_timestamp) - timedelta(minutes=TOKEN_EXPIRY_GAP_MINUTES)

            # renew oesp token
            if now >= expiry_date:
                self.refresh_token()

    def _register_device(self, device_id):
        json_payload = {
            "deviceId": device_id,
            "deviceName": DEVICE_NAME,
            "customerDefinedName": DEVICE_NAME,
            "deviceClass": DEVICE_CLASS
        }

        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/devices",
            headers=self.construct_header(),
            data=json_payload)

        if r.status_code != 204:
            self.logger.error("An error has occurred trying to register the device.")

    def get_server_certificate(self, content_locator):
        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/license/eme",
            headers={
                "User-Agent": self.USER_AGENT,
                "Connection": 'keep-alive',
                "Referer": "https://www.telenettv.be/",
                "Content-Type": "application/octet-stream",
                "X-OESP-Content-Locator": content_locator,
                "X-OESP-DRM-SchemeIdUri": "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed",
                "X-OESP-License-Token": self.license_token,
                "X-OESP-License-Token-Type": "velocix",
                "X-OESP-Token": self.oesp_token,
                "X-OESP-Username": self.username
            },
            data="\b\x04",
            is_json=False
        )

        return base64.b64encode(r.content)
