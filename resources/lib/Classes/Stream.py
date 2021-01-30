from resources.lib.Utils import Utils


class Stream(object):
<<<<<<< HEAD
    BASE_URL_MPD = "https://{}/dash/{};vxttoken={}/manifest.mpd"
    BASE_URL_HSS = "https://{}/ss/{};vxttoken={}/Manifest"
    BASE_URL_HLS = "https://{}/hls/streams/{};vxttoken={}/index.m3u8"
=======
    BASE_URL_MPD = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/dash/{};vxttoken={}/manifest.mpd"
    BASE_URL_HSS = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/ss/{};vxttoken={}/Manifest"
    BASE_URL_HLS = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/hls/streams/{};vxttoken={}/index.m3u8"
>>>>>>> c31fd948d956a294f41647f99afecc5c7c8e6ae6

    def __init__(self, stream_url, content_locator, protection_key):
        self.baseUrl = Utils.get_domain_url(stream_url)
        self.streamUrl = stream_url
        self.contentLocator = content_locator
        self.protectionKey = protection_key
