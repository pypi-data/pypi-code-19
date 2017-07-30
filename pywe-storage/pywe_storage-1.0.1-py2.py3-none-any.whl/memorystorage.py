# -*- coding: utf-8 -*-

from .basestorage import BaseStorage


class MemoryStorage(BaseStorage):

    def __init__(self, prefix='pywe'):
        self._data = {}
        self.prefix = prefix

    def key_name(self, key):
        return '{0}:{1}'.format(self.prefix, key)

    def get(self, key, default=None):
        return self._data.get(self.key_name(key), default)

    def set(self, key, value, ttl=None):
        if value is None:
            return
        self._data[self.key_name(key)] = value

    def delete(self, key):
        self._data.pop(self.key_name(key), None)
