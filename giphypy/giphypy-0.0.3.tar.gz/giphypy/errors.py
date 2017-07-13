class GiphyPyKeyError(Exception):
    msg = 'Missing Giphy api_key, ' \
          'visit:https://developers.giphy.com ' \
          'to obtain an api_key'

    def __str__(self):
        return self.msg


class GiphyBaseError(Exception):
    def __init__(self, msg):
        self.msg = msg


class GiphyPyError(GiphyBaseError):
    def __init__(self, msg):
        super().__init__(msg)

    def __str__(self):
        return self.msg
