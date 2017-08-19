# -*- coding:utf-8 -*-


class Response(object):
    """
    views返回值
    """

    def __init__(self, status_code, appinfo=None, message=None):
        self.code = status_code
        self.appinfo = appinfo
        self.message = message
        if appinfo is None:
            self.appinfo = {}

        if message is None:
            self.message = ''


class Success(Response):
    """
    成功返回值
    """

    def __init__(self, appinfo):
        super(Success, self).__init__(200, appinfo)


class Failure(Response):
    """
    失败返回值
    """

    def __init__(self, status_code, message):
        super(Failure, self).__init__(status_code, message=message)


_200_SUCCESS = 200
_400_BAD_REQUEST = 400
_404_NOT_FOUND = 404
