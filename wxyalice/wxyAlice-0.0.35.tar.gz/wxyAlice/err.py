from sanic.exceptions import ServerError, InvalidUsage


class Err(object):
    def __init__(self, msg='some thing wrong', code=500):
        if code == 400:
            raise InvalidUsage(msg)
        raise ServerError(msg)
