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

    def construct_header(self, content_type='application/json'):
        header = {
            'Accept': content_type,
            'Content-Type': content_type,
            'User-Agent': self.USER_AGENT,
            'DNT': '1'
        }

        return header

    def login(self):
        r = Utils.make_request(
            self.session,
            method="POST",
            url="https://login.prd.telenet.be/openid/login.do",
            headers=self.construct_header(content_type="application/x-www-form-urlencoded"),
            data={
                'j_username': '{}'.format(self.username),
                'j_password': '{}'.format(self.passwd),
                'rememberme': 'true'
            }, is_json=False)

        last_response = r.history[-1]

        if "Location" in last_response.headers:
            token = Utils.extract_auth_token(last_response.headers.get('Location'))

            PluginCache.set_data({
                "token": token,
                "username": self.username
            })

    def authorize(self):
        Utils.make_request(
            self.session,
            method="GET",
            url=self.authorization_uri,
            headers={'User-Agent': self.USER_AGENT},
            allow_redirects=False)

    def web_authorization(self):
        r = Utils.make_request(
            self.session,
            method="GET",
            url="https://obo-prod.oesp.telenettv.be/oesp/v4/BE/nld/web/authorization",
            headers=self.construct_header())

        json_data = r.json()

        self.authorization_uri = json_data["session"]["authorizationUri"]

        validity_token = json_data["session"]["validityToken"]
        state = json_data["session"]["state"]

        PluginCache.set_data({
            "validityToken": validity_token,
            "state": state
        })
