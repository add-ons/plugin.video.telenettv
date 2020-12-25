import json
import os
import xbmc
from xbmcaddon import Addon


class PluginCache:
    CACHE_FILE_NAME = "data.json"

    @classmethod
    def key_exists(cls, key):

        path = xbmc.translatePath(Addon().getAddonInfo('profile')).decode("utf-8")

        if not os.path.isfile(os.path.join(path, cls.CACHE_FILE_NAME)):
            return False

        with open(os.path.join(path, cls.CACHE_FILE_NAME), "r") as json_file:
            data = json.load(json_file)

        return key in data

    @classmethod
    def set_data(cls, json_data):
        path = xbmc.translatePath(Addon().getAddonInfo('profile')).decode("utf-8")

        if not os.path.exists(path):
            os.mkdir(path, 0o775)

        data = {}
        if os.path.isfile(os.path.join(path, cls.CACHE_FILE_NAME)):
            with open(os.path.join(path, cls.CACHE_FILE_NAME), "r") as json_file:
                data = json.load(json_file)

        data.update(json_data)

        with open(os.path.join(path, cls.CACHE_FILE_NAME), "w") as json_file:
            json.dump(data, json_file)

    @classmethod
    def get_by_key(cls, key):
        path = xbmc.translatePath(Addon().getAddonInfo('profile')).decode("utf-8")

        try:
            with open(os.path.join(path, cls.CACHE_FILE_NAME), "r") as json_file:
                data = json.load(json_file)

            return data.get(key)
        except (IOError, KeyError):
            return ""
