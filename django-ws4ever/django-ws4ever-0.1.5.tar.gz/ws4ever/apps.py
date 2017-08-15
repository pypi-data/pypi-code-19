import importlib
import logging
import os

import gevent
import redis
from django.apps import AppConfig
from django.conf import settings
from django.utils.encoding import force_str

from ws4ever.redis import CH_WEBSOCKET_NOTIFY
from ws4ever.helpers import import_module

log = logging.getLogger('ws4ever')


class WS4EverConfig(AppConfig):
    name = 'ws4ever'

    def ready(self):
        self.add_period_task(self.subscribe_redis, 1)

    @classmethod
    def add_period_task(cls, func, interval: float):
        def exec_func():
            while True:
                gevent.sleep(interval)
                try:
                    func()
                except:
                    log.exception("exec fun exception %s", str(func))

        return gevent.spawn(exec_func)

    @classmethod
    def subscribe_redis(cls):
        log.info('start subscribe, pid:%s', os.getpid())
        r = redis.StrictRedis(settings.WS4EVER['BROADCAST_BACKEND']['REDIS_HOST'],
                              password=settings.WS4EVER['BROADCAST_BACKEND']['REDIS_HOST'])
        p = r.pubsub(ignore_subscribe_messages=True)
        p.psubscribe("*")
        for message in p.listen():
            cls.handle_redis_message(message)

    @classmethod
    def handle_redis_message(cls, m):
        try:
            channel, data = (force_str(m.get(x, b'')) for x in ['channel', 'data'])
            if channel == CH_WEBSOCKET_NOTIFY:
                for handlers in settings.WS4EVER['ROUTES'].values():
                    import_module(handlers).on_redis_message(data)
            else:
                log.warning("unexpected redis message channel: %s data: %s", channel, data)
        except:
            log.exception('handle_redis_message')
