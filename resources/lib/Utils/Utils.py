from urlparse import urlparse


def extract_auth_token(url):
    callback_key = regex(r"(?<=code=)\w{0,32}", url)
    return callback_key


def regex(query, text):
    import re
    try:
        return re.findall(r"%s" % query, text)[0]
    except IndexError:
        return None


def create_guid():
    import uuid
    return str(uuid.uuid4())


def create_token(size):
    import binascii, os

    size = int(size / 2)
    return binascii.hexlify(os.urandom(size)).decode()


def get_datetime(timestamp):
    from datetime import datetime, timedelta

    timestamp /= 1000
    date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
    return date


def utc2local(utc):
    import time
    from datetime import datetime

    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset


def get_domain_url(url):
    from urlparse import urlparse
    domain = urlparse(url).netloc
    return domain


def make_request(session, method, url, headers, data="", is_json=True, allow_redirects=True, additional_cookies=None):
    import json

    if method == "POST":
        r = session.post(url,
                         headers=headers,
                         data=json.dumps(data) if is_json else data,
                         allow_redirects=allow_redirects,
                         cookies=additional_cookies)
    elif method == "PUT":
        r = session.put(url,
                        headers=headers,
                        data=json.dumps(data) if is_json else data,
                        allow_redirects=allow_redirects,
                        cookies=additional_cookies)
    elif method == "GET":
        r = session.get(url,
                        headers=headers,
                        allow_redirects=allow_redirects,
                        cookies=additional_cookies)
    else:
        r = None

    return r
