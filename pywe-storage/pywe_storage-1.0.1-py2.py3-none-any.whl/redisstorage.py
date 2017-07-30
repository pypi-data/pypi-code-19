# -*- coding: utf-8 -*-

import json

from pywe_utils import to_text

from .basestorage import BaseStorage


class RedisStorage(BaseStorage):

    def __init__(self, redis, prefix='pywe'):
        for method_name in ('get', 'set', 'delete'):
            assert hasattr(redis, method_name)
        self.redis = redis
        self.prefix = prefix

    def key_name(self, key):
        return '{0}:{1}'.format(self.prefix, key)

    def get(self, key, default=None):
        value = self.redis.get(self.key_name(key))
        if value is None:
            return default
        return json.loads(to_text(value))

    def set(self, key, value, ttl=None):
        if value is None:
            return
        self.redis.set(self.key_name(key), json.dumps(value), ex=ttl)

    def delete(self, key):
        self.redis.delete(self.key_name(key))
