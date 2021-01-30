from resources.lib.Utils import Utils


class Stream(object):
    BASE_URL_MPD = "https://{}/dash/{};vxttoken={}/manifest.mpd"
    BASE_URL_HSS = "https://{}/ss/{};vxttoken={}/Manifest"
    BASE_URL_HLS = "https://{}/hls/streams/{};vxttoken={}/index.m3u8"


    def __init__(self, stream_url, content_locator, protection_key):
        self.baseUrl = Utils.get_domain_url(stream_url)
        self.streamUrl = stream_url
        self.contentLocator = content_locator
        self.protectionKey = protection_key
