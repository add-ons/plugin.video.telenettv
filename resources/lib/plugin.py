# -*- coding: utf-8 -*-
import base64
import inputstreamhelper
import requests
import routing
import logging
import xbmcaddon
from resources.lib import kodilogging
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItems, endOfDirectory, setResolvedUrl
<<<<<<< HEAD
from resources.lib.Classes.Exceptions.DeviceLimitReachedException import DeviceLimitReachedException
from resources.lib.kodiwrapper import KodiWrapper
=======
>>>>>>> c31fd948d956a294f41647f99afecc5c7c8e6ae6

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib2 import quote

from resources.lib.TelenetTV import TelenetTV
from resources.lib.Classes.StreamingFormat import StreamingFormat

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))
kodilogging.config()
plugin = routing.Plugin()

DRM = 'com.widevine.alpha'
LICENSE_URL = 'https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/license/eme'

session = requests.session()
session.verify = False
tv = TelenetTV(session, logger)


@plugin.route('/')
def index():
    channels = tv.get_channels()

    listing = []
    for channel in channels:
        list_item = ListItem()
        list_item.setLabel(channel.title)
        list_item.setArt(
            {
                'fanart': channel.stream_thumbnail,
                'icon': channel.thumbnail,
                'thumb': channel.thumbnail
            })

        list_item.setInfo('video', {'title': channel.title})
        list_item.setProperty('IsPlayable', "true")

        streaming_format = StreamingFormat.get_streaming_format()
        if streaming_format == StreamingFormat.SMOOTH_STREAM:
<<<<<<< HEAD
            stream_base_url = channel.stream_HLS.baseUrl
            content_locator = channel.stream_HLS.contentLocator
            protection_key = channel.stream_HLS.protectionKey
        else:
            stream_base_url = channel.stream_DASH.baseUrl
=======
            content_locator = channel.stream_HLS.contentLocator
            protection_key = channel.stream_HLS.protectionKey
        else:
>>>>>>> c31fd948d956a294f41647f99afecc5c7c8e6ae6
            content_locator = channel.stream_DASH.contentLocator
            protection_key = channel.stream_DASH.protectionKey

        listing.append((plugin.url_for(play_channel,
<<<<<<< HEAD
                                       base_uri=stream_base_url,
=======
>>>>>>> c31fd948d956a294f41647f99afecc5c7c8e6ae6
                                       content_locator=content_locator,
                                       protection_key=protection_key), list_item, False))

    addDirectoryItems(plugin.handle, listing, len(listing))
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/play/locator/<base_uri>/<content_locator>/key/<protection_key>')
def play_channel(base_uri, content_locator, protection_key):
    try:
        tv.request_license_token(content_locator)
    except DeviceLimitReachedException as ex:
        return KodiWrapper.error_dialog(str(ex))

    streaming_format = StreamingFormat.get_streaming_format()
    if streaming_format == StreamingFormat.MPEG_DASH:
        protocol = "mpd"
    elif streaming_format == StreamingFormat.SMOOTH_STREAM:
        protocol = "ism"
    else:
        protocol = ""

    is_helper = inputstreamhelper.Helper(protocol, drm=DRM)
    if is_helper.check_inputstream():
<<<<<<< HEAD
        manifest_url = tv.create_manifest_url(base_uri, protection_key)
=======
        manifest_url = tv.create_manifest_url(protection_key)
>>>>>>> c31fd948d956a294f41647f99afecc5c7c8e6ae6

        play_item = ListItem(path=manifest_url)
        play_item.setContentLookup(False)
        play_item.setMimeType('application/dash+xml')

        server_certificate = tv.get_server_certificate(content_locator)

        play_item.setProperty('inputstream.adaptive.server_certificate', server_certificate)
        play_item.setProperty('inputstream.adaptive.license_flags', 'persistent_storage')
        play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
        play_item.setProperty('inputstream.adaptive.manifest_type', protocol)
        play_item.setProperty('inputstream.adaptive.license_type', DRM)
        play_item.setProperty('inputstream.adaptive.license_key',
                              '%(url)s|'
                              'User-Agent=%(ua)s'
                              '&Connection=keep-alive'
                              '&Referer=https://www.telenettv.be/'
                              '&Content-Type=application/octet-stream'
                              '&X-OESP-Content-Locator=%(oespContentLoc)s'
                              '&X-OESP-DRM-SchemeIdUri=%(schemeId)s'
                              '&X-OESP-License-Token=%(oespLicToken)s'
                              '&X-OESP-License-Token-Type=%(oespLicTokenType)s'
                              '&X-OESP-Token=%(oespToken)s'
                              '&X-OESP-Username=%(oespUsername)s'
                              '&X-OESP-Profile-Id=%(profileId)s'
                              '|%(payload)s|'
                              % dict(
                                  url=LICENSE_URL,
                                  ua=quote(tv.USER_AGENT),
                                  schemeId="urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed",
                                  oespToken=tv.oesp_token,
                                  oespUsername=tv.username,
                                  oespLicToken=tv.license_token,
                                  oespContentLoc=content_locator,
                                  oespLicTokenType="velocix",
                                  payload="R{SSM}",
                                  deviceId=tv.device_id,
                                  profileId = tv.shared_profile_id
                              ))
        setResolvedUrl(plugin.handle, True, listitem=play_item)


def run():
    plugin.run()