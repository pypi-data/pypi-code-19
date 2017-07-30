# -*- coding: utf-8 -*-

from .basestorage import BaseStorage


class ShoveStorage(BaseStorage):

    def __init__(self, shove, prefix='pywe'):
        self.shove = shove
        self.prefix = prefix

    def key_name(self, key):
        return '{0}:{1}'.format(self.prefix, key)

    def get(self, key, default=None):
        try:
            return self.shove[self.key_name(key)]
        except KeyError:
            return default

    def set(self, key, value, ttl=None):
        if value is None:
            return
        self.shove[self.key_name(key)] = value

    def delete(self, key):
        try:
            del self.shove[self.key_name(key)]
        except KeyError:
            pass
