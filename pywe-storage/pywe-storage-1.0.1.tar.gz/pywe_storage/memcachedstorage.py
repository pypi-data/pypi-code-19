# -*- coding: utf-8 -*-

import json

from pywe_utils import to_text

from .basestorage import BaseStorage


class MemcachedStorage(BaseStorage):

    def __init__(self, mc, prefix='pywe'):
        for method_name in ('get', 'set', 'delete'):
            assert hasattr(mc, method_name)
        self.mc = mc
        self.prefix = prefix

    def key_name(self, key):
        return '{0}:{1}'.format(self.prefix, key)

    def get(self, key, default=None):
        value = self.mc.get(self.key_name(key))
        if value is None:
            return default
        return json.loads(to_text(value))

    def set(self, key, value, ttl=None):
        if value is None:
            return
        self.mc.set(self.key_name(key), json.dumps(value))

    def delete(self, key):
        self.mc.delete(self.key_name(key))
