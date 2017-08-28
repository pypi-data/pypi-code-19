import logging
import ujson as json
from urllib.parse import urlparse

import gevent
import redis
from django.conf import settings
from django.utils.encoding import force_str

from ws4ever.helpers import import_module

log = logging.getLogger('ws4ever')

BROADCAST_METHOD_REDIS = 'REDIS'
BROADCAST_METHOD_MEMORY = 'MEMORY'
CH_WEBSOCKET_NOTIFY = 'websocket:notify'  # 发送广播


class BaseBackend:
    def __init__(self, backend_url, routes):
        self.backend_url = urlparse(backend_url)
        self.routes = routes

        self.setup()

    def setup(self):
        """ 在app中调用，进行一些一次性的初始化设置（如收听redis消息）"""
        pass

    def notify_clients(self, kind, payload=None, **extra):
        """ 给所有的websocket Client发通知 """
        data = {
            "kind": kind,
        }
        if payload is not None:
            data['payload'] = payload
        if extra:
            data['extra'] = extra
        return self._do_notify(data)

    def _do_notify(self, data):
        """ 将data publish出去，后续 self._on_notify 会收到 """
        raise NotImplementedError

    def _on_notify(self, data):
        for handler in self.routes.values():
            import_module(handler).on_notify(data['kind'], data.get('payload'), **data.get('extra', {}))


class MemoryBackend(BaseBackend):
    def _do_notify(self, data):
        return self._on_notify(data)


class RedisBackend(BaseBackend):
    def __init__(self, backend_url, routes):
        super(RedisBackend, self).__init__(backend_url, routes)
        self.sender = self._make_client()

    def setup(self):
        def exec_func():
            while True:
                gevent.sleep(1)
                try:
                    subscriber = self._make_client()
                    p = subscriber.pubsub(ignore_subscribe_messages=True)
                    p.psubscribe("*")
                    for message in p.listen():
                        self._handle_redis_message(message)
                except:
                    log.exception("exec subscribe message exception")

        return gevent.spawn(exec_func)

    def _do_notify(self, data):
        return self.sender.publish(CH_WEBSOCKET_NOTIFY, json.dumps(data))

    def _make_client(self):
        return redis.StrictRedis(self.backend_url.hostname,
                                 password=self.backend_url.password,
                                 decode_responses=True,
                                 db=0)

    def _handle_redis_message(self, m):
        try:
            channel, data = (force_str(m.get(x, b'')) for x in ['channel', 'data'])
            data = json.loads(data)
            if channel == CH_WEBSOCKET_NOTIFY:
                self._on_notify(data)
        except:
            log.exception('handle_redis_message')


backend_cache = {}


def _get_backend(backend_url, routes):
    # 优先从cache中获得Backend，并使用最新的routes
    backend = backend_cache.get(backend_url)
    if backend:
        backend.routes = routes
        return backend

    # 如果不在cache中，就创建backend，并缓存起来
    backend_url_lower = backend_url.lower()
    if backend_url_lower == 'memory':
        backend = MemoryBackend(backend_url_lower, routes)

    elif backend_url_lower.startswith('redis'):
        backend = RedisBackend(backend_url_lower, routes)

    else:
        raise Exception('invalid backend: {}'.format(backend_url))

    backend_cache[backend_url] = backend

    return backend


def get_backend():
    return _get_backend(settings.WS4EVER['NOTIFY_BACKEND'], settings.WS4EVER['ROUTES'])


def notify_clients(kind, payload=None, **extra):
    return get_backend().notify_clients(kind, payload, **extra)
