from xbmcaddon import Addon


class StreamingFormat(object):
    MPEG_DASH = 0
    SMOOTH_STREAM = 1

    @classmethod
    def get_streaming_format(cls):
        setting = Addon().getSetting('streamingFormat')

        if setting == "MPEG Dash":
            return cls.MPEG_DASH
        elif setting == "Smoothstream":
            return cls.SMOOTH_STREAM

