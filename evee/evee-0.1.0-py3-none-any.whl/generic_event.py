from collections import MutableMapping
from evee.event import Event


class GenericEvent(Event, MutableMapping):
    def __init__(self, subject=None, arguments: dict = None):
            super().__init__()
            if arguments:
                self._arguments = arguments
            else:
                self._arguments = {}
            self.__subject = subject

    def get_subject(self):
        return self.__subject

    def get_argument(self, key):
        try:
            return self[key]
        except KeyError:
            raise KeyError('Argument "{}" not found.'.format(key))

    def set_argument(self, key, value):
        self[key] = value

    def get_arguments(self):
        return dict(self._arguments)

    def set_arguments(self, args: dict = None):
        if args:
            self._arguments = args
        return self

    def has_argument(self, key):
        return key in self

    def __delitem__(self, key):
        del(self._arguments[key])

    def __setitem__(self, key, value):
        self._arguments[key] = value

    def __iter__(self):
        return iter(self._arguments)

    def __getitem__(self, key):
        return self._arguments[key]

    def __len__(self):
        return len(self._arguments)
