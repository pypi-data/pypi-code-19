#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import ujson
from .config import config


class Redisfun(object):

    def __init__(self, redis_url):
        self.redis_conn = redis.from_url(redis_url)

    def get_sess_str(self, mysess):
        return self.redis_conn.get(''.join(['sess:', mysess]))

    def set_val(self, k, v, sec):
        if isinstance(v, basestring):
            self.redis_conn.set(k, v, sec)
        elif isinstance(v, (list, dict)):
            self.redis_conn.set(k, ujson.dumps(v, ensure_ascii=False), sec)

redisfun = Redisfun(config['redis'])
