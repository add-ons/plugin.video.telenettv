from xbmcaddon import Addon


class Credentials:
    @staticmethod
    def get_password():
        return Addon().getSetting('password')

    @staticmethod
    def get_username():
        return Addon().getSetting('username')

    @classmethod
    def are_filled_in(cls):
        return not (cls.get_username() is None or cls.get_password() is None
                    or cls.get_username() == '' or cls.get_password() == '')

