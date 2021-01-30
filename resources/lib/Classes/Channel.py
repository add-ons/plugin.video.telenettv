class Channel(object):
    def __init__(self, channel_id, station_id, title, channel_nr, has_live_stream, entitlements,
                 stream_dash="", stream_hls="", stream_hss=""):
        self.channel_id = channel_id
        self.station_id = station_id
        self.title = title
        self.channelNumber = channel_nr
        self.hasLiveStream = has_live_stream
        self.entitlements = entitlements
        self.sort_entitlements()

        self.stream_DASH = stream_dash
        self.stream_HLS = stream_hls
        self.stream_HSS = stream_hss

        self.thumbnail = ""
        self.stream_thumbnail = ""

    def sort_entitlements(self):
        self.entitlements.sort()
