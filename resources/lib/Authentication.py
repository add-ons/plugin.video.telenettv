from resources.lib.Utils import Utils
from resources.lib.Utils.PluginCache import PluginCache
from resources.lib.Classes.Credentials import Credentials


class Authentication(object):
    REDIRECT_URI = "https://www.telenettv.be/nl/login_success"
    USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.138 Safari/537.36')

    CLIENT_ID = "1.4.29.11||{}".format(USER_AGENT)

    def __init__(self, session):
        self.session = session
        self.authorization_uri = ""

        self.username = Credentials.get_username()
        self.passwd = Credentials.get_password()

    def login(self):
        HEADER = {
            'User-Agent': self.USER_AGENT,
            'X-Client-Id': self.CLIENT_ID
        }

        r = self.session.post("https://login.prd.telenet.be/openid/login.do",
                              data={
                                  'j_username': '{}'.format(self.username),
                                  'j_password': '{}'.format(self.passwd)
                              }, headers=HEADER)

        last_response = r.history[-1]

        if "Location" in last_response.headers:
            token = Utils.extract_auth_token(last_response.headers.get('Location'))

            PluginCache.set_data({
                "token": token,
                "username": self.username
            })

    def authorize(self):
        self.session.get(self.authorization_uri,
                         allow_redirects=False)

    def web_authorization(self):
        HEADER = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT,
            'DNT': '1'
        }

        r = self.session.get("https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/authorization", headers=HEADER)

        json = r.json()

        self.authorization_uri = json["session"]["authorizationUri"]

        validity_token = json["session"]["validityToken"]
        state = json["session"]["state"]

        PluginCache.set_data({
            "validityToken": validity_token,
            "state": state
        })






