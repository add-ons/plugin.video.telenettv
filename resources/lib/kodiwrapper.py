from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItems, endOfDirectory, setResolvedUrl


class KodiWrapper(object):

    @classmethod
    def info_dialog(cls, title, message):
        dialog = Dialog()
        return dialog.ok(title, message)

    @classmethod
    def error_dialog(cls, message):
        dialog = Dialog()
        return dialog.ok("Error", message)

    @classmethod
    def yes_no_dialog(cls, title, message):
        dialog = Dialog()
        result = dialog.yesno(title, message)
        return result



