class Stream(object):
    BASE_URL_MPD = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/dash/{};vxttoken={}/manifest.mpd"
    BASE_URL_HSS = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/ss/{};vxttoken={}/Manifest"
    BASE_URL_HLS = "https://wp1-halo01-vxtoken-live-be-prod.tnprod.cdn.dmdsdp.com/hls/streams/{};vxttoken={}/index.m3u8"

    def __init__(self, stream_url, content_locator, protection_key):
        self.streamUrl = stream_url
        self.contentLocator = content_locator
        self.protectionKey = protection_key
