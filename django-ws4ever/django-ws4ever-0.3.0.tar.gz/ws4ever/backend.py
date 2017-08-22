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

backend_conf = urlparse(settings.WS4EVER['NOTIFY_BACKEND'])
if backend_conf.scheme == 'redis':
    redis_client = redis.StrictRedis(backend_conf.hostname, password=backend_conf.password, decode_responses=True,
                                     db=0)
    broadcast_method = BROADCAST_METHOD_REDIS
else:
    broadcast_method = BROADCAST_METHOD_MEMORY


def notify_clients(kind, payload=None, **extra):
    """ 给所有的websocket Client发通知 """
    data = {
        "kind": kind,
    }
    if payload is not None:
        data['payload'] = payload
    if extra:
        data['extra'] = extra
    return _publish(data)


def _publish(data):
    if broadcast_method == BROADCAST_METHOD_REDIS:
        return redis_client.publish(CH_WEBSOCKET_NOTIFY, json.dumps(data))
    else:
        handle_notify(data)


def handle_notify(data):
    for handler in settings.WS4EVER['ROUTES'].values():
        import_module(handler).on_notify(data['kind'], data.get('payload'), **data.get('extra', {}))


def subscribe_message():
    if broadcast_method == BROADCAST_METHOD_REDIS:
        def exec_func():
            while True:
                gevent.sleep(1)
                try:
                    subscribe_message()
                except:
                    log.exception("exec subscribe message exception")
        return gevent.spawn(exec_func)
    else:
        #if memory, do nothing
        return


def handle_redis_message(m):
    try:
        channel, data = (force_str(m.get(x, b'')) for x in ['channel', 'data'])
        data = json.loads(data)
        if channel == CH_WEBSOCKET_NOTIFY:
            handle_notify(data)
        else:
            log.warning("unexpected redis message channel: %s data: %s", channel, data)
    except:
        log.exception('handle_redis_message')


def subscribe_redis_message():
    assert broadcast_method == BROADCAST_METHOD_REDIS, "backend is supposed to be redis"
    backend_conf = urlparse(settings.WS4EVER['NOTIFY_BACKEND'])
    r = redis.StrictRedis(backend_conf.hostname, password=backend_conf.password)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.psubscribe("*")
    for message in p.listen():
        handle_redis_message(message)


# just for test
def refresh_backend_conf():
    global redis_client, broadcast_method
    backend_conf = urlparse(settings.WS4EVER['NOTIFY_BACKEND'])
    if backend_conf.scheme == 'redis':
        redis_client = redis.StrictRedis(backend_conf.hostname, password=backend_conf.password, decode_responses=True,
                                         db=0)
        broadcast_method = BROADCAST_METHOD_REDIS
    else:
        broadcast_method = BROADCAST_METHOD_MEMORY
