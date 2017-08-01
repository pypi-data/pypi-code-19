class BookItError(Exception):
    def __repr__(self):
        return f'{self.__class__.__name__} ({self.__dict__})'


class BookItLoginFailedError(BookItError):
    def __init__(self, username):
        self.username = username
