import importlib
import logging
import os
import gevent
from django.apps import AppConfig
from django.conf import settings
import redis
from django.utils.encoding import force_str

from ws4ever.redis import CH_WEBSOCKET_NOTIFY

log = logging.getLogger('ws4ever')


class Ws4EverConfig(AppConfig):
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
        r = redis.StrictRedis(settings.REDIS_HOST, password=settings.REDIS_PASSWORD)
        p = r.pubsub(ignore_subscribe_messages=True)
        p.psubscribe("*")
        for message in p.listen():
            cls.handle_redis_message(message)

    @classmethod
    def handle_redis_message(cls, m):
        # from main.websocket import WebSocketClientApplication
        try:
            channel, data = (force_str(m.get(x, b'')) for x in ['channel', 'data'])
            if channel == CH_WEBSOCKET_NOTIFY:
                for handlers in settings.WEBSOCKET_PATHS.values():
                    importlib.import_module(handlers).on_redis_message(data)
            else:
                log.warning("unexpected redis message channel: %s data: %s", channel, data)
        except:
            log.exception('handle_redis_message')
