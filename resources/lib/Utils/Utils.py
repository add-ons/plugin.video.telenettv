def get_json(response):
    return response.json()


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
