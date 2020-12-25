import json as jsn
from resources.lib.Authentication import Authentication
from resources.lib.Utils import Utils
from resources.lib.Classes.Channel import Channel
from resources.lib.Classes.Stream import Stream
from resources.lib.Utils.PluginCache import PluginCache

DEVICE_NAME = "Mijn computer - Google Chrome"
DEVICE_CLASS = "desktop"

if not PluginCache.key_exists("deviceId"):
    PluginCache.set_data({"deviceId": "fe88cd8ace897d72c78441f648a2f92a4e298cced867179932d7c2751d79fb83"})


class TelenetTV(Authentication):
    def __init__(self, session, logger_instance=None):
        super(self.__class__, self).__init__(session)

        if self.must_login():
            self.web_authorization()
            self.authorize()
            self.login()
            self.request_tokens()

        self.oesp_token = PluginCache.get_by_key("oespToken")
        self.shared_profile_id = PluginCache.get_by_key("sharedProfileId")
        self.license_token = ""
        self.logger = logger_instance

        self.device_id = PluginCache.get_by_key("deviceId")

    @staticmethod
    def must_login():
        return not PluginCache.key_exists("oespToken") or not PluginCache.key_exists("token")

    def resume_session(self):
        username = PluginCache.get_by_key("username")
        oesp_token = PluginCache.get_by_key("oespToken")

        HEADER = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OESP-Token': oesp_token,
            'X-OESP-Username': username
        }

        r = self.session.get("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/session", headers=HEADER)

        json = r.json()

        return json["oespToken"]

    def get_location_id(self):
        r = self.session.get("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/session")
        json = Utils.get_json(r)

        if "locationId" in json:
            return json["locationId"]

        return None

    def get_channels(self):
        r = self.session.get("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/channels?"
                             "byLocationId={}"
                             "&includeInvisible=false"
                             "&sort=channelNumber"
                             .format(self.get_location_id()))

        json = Utils.get_json(r)

        useful_channel_data = []
        if "channels" in json:
            fetched_channel_data = json["channels"]
            for channel_data in fetched_channel_data:
                station = channel_data["stationSchedules"][0]["station"]
                video_streams = station["videoStreams"]

                if video_streams:
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

                    channel = Channel(channel_data["title"],
                                      channel_data["channelNumber"],
                                      bool(station["hasLiveStream"]),
                                      station["entitlements"],
                                      DASH_stream,
                                      HLS_stream,
                                      HSS_stream)

                    thumbnail = [img["url"] for img in station["images"]
                                 if img["assetType"] == "station-logo-xlarge"][0]

                    imageStream = [img["url"] for img in station["images"]
                                   if img["assetType"] == "imageStream"][0]

                    channel.thumbnail = thumbnail
                    channel.stream_thumbnail = imageStream

                    useful_channel_data.append(channel)

        return useful_channel_data

    def request_tokens(self):
        self._get_refresh_token()
        self._get_oesp_token()

    def clear_streams(self):
        HEADER = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OESP-Token': self.oesp_token,
            'X-OESP-Username': self.username,
            'X-OESP-Profile-Id': self.shared_profile_id
        }

        r = self.session.post("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/playback/clearstreams",
                              headers=HEADER)

    def check_registered_devices(self, device_id):
        HEADER = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OESP-Token': self.oesp_token,
            'X-OESP-Username': self.username,
            'X-OESP-Profile-Id': self.shared_profile_id
        }

        r = self.session.get("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/devices/status", headers=HEADER)

        json = r.json()

        currentRegisteredDevices = int(json["currentRegisteredDevices"])
        maxRegisteredDevices = int(json["maxRegisteredDevices"])

        if currentRegisteredDevices < maxRegisteredDevices:
            self._register_device(device_id)

    def replace_registered_device(self, old_device_id, new_device_id):
        HEADER = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OESP-Token': self.oesp_token,
            'X-OESP-Username': self.username,
            'X-OESP-Profile-Id': self.shared_profile_id,
            'X-Client-Id': self.CLIENT_ID
        }

        data = {
            "deviceId": new_device_id,
            "deviceName": DEVICE_NAME,
            "customerDefinedName": DEVICE_NAME,
            "deviceClass": DEVICE_CLASS
        }

        r = self.session.put("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/devices/{}".format(old_device_id),
                             data=jsn.dumps(data),
                             headers=HEADER)

        json = r.json()

        return json["deviceId"]

    def request_license_token(self, content_locator):
        if PluginCache.key_exists("oespToken"):
            self.resume_session()

        HEADER = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OESP-Token': self.oesp_token,
            'X-OESP-Username': self.username,
            'X-OESP-Profile-Id': self.shared_profile_id,
            'X-Client-Id': self.CLIENT_ID
        }

        json = {
            "contentLocator": content_locator,
            "deviceId": self.device_id
        }

        r = self.session.post("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/license/token",
                              data=jsn.dumps(json), headers=HEADER)
        try:
            json = r.json()

            if r.status_code == 200:
                license_token = json["token"]

                PluginCache.set_data({
                    "licenseToken": license_token
                })
            elif r.status_code == 400:
                error_obj = json[0]
                if "code" in error_obj and error_obj["code"] == "deviceUnregistered":
                    self.check_registered_devices(self.device_id)
                elif "code" in error_obj and error_obj["code"] == "deviceUnregisteredDeviceLimitReached":
                    deviceId = self.replace_registered_device(self.device_id, Utils.create_token(64))

                    PluginCache.set_data({
                        "deviceId": deviceId
                    })

                self.request_license_token(content_locator)
        except KeyError:
            self.logger.error("There was a problem with the JSON Package")

    def create_manifest_url(self, channel):
        self.license_token = PluginCache.get_by_key("licenseToken")

        url = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/ss/{};vxttoken={}/Manifest" \
            .format(channel, self.license_token)

        print("KIJK", url)

        return url

    def _get_refresh_token(self):
        HEADER = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT,
            'DNT': '1'
        }

        token = PluginCache.get_by_key("token")
        validity_token = PluginCache.get_by_key("validityToken")
        state = PluginCache.get_by_key("state")

        data = {
            "authorizationGrant":
                {
                    "authorizationCode": token,
                    "validityToken": validity_token,
                    "state": state
                }
        }

        r = self.session.post("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/authorization",
                              data=jsn.dumps(data), headers=HEADER)

        json = r.json()

        refresh_token = json["refreshToken"]

        PluginCache.set_data({
            "refreshToken": refresh_token,
        })

    def _get_oesp_token(self):
        HEADER = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT,
            'DNT': '1'
        }

        refresh_token = PluginCache.get_by_key("refreshToken")

        data = {
            "refreshToken": refresh_token,
            "username": self.username
        }

        r = self.session.post("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/session?token=true",
                              data=jsn.dumps(data), headers=HEADER)

        json = r.json()

        oesp_token = json["oespToken"]
        shared_profile_id = json["customer"]["sharedProfileId"]

        PluginCache.set_data({
            "oespToken": oesp_token,
            "sharedProfileId": shared_profile_id
        })

    def _register_device(self, device_id):
        HEADER = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OESP-Token': self.oesp_token,
            'X-OESP-Username': self.username,
            'X-OESP-Profile-Id': self.shared_profile_id
        }

        data = {
            "deviceId": device_id,
            "deviceName": DEVICE_NAME,
            "customerDefinedName": DEVICE_NAME,
            "deviceClass": DEVICE_CLASS
        }

        r = self.session.post("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/devices",
                              data=jsn.dumps(data),
                              headers=HEADER)

        if r.status_code != 204:
            self.logger.error("An error has occurred trying to register the device.")

