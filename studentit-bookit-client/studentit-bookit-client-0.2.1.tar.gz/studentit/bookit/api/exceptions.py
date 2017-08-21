class BookItError(Exception):
    def __repr__(self):
        return '{} ({})'.format(self.__class__.__name__, self.__dict__)


class BookItLoginFailedError(BookItError):
    def __init__(self, username):
        self.username = username
