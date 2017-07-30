from sanic.exceptions import ServerError, InvalidUsage


class Err(object):
    def __init__(self, code=500, msg='some thing wrong'):
        if code == 400:
            raise InvalidUsage(msg, code)
        raise ServerError(msg, code)
