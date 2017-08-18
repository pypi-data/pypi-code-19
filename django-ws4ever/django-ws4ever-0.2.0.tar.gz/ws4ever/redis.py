import ujson as json
from urllib.parse import urlparse

import redis
from django.conf import settings

backend_conf = urlparse(settings.WS4EVER['BROADCAST_BACKEND'])
redis_client = redis.StrictRedis(backend_conf.hostname, password=backend_conf.password, decode_responses=True, db=0)
CH_WEBSOCKET_NOTIFY = 'websocket:notify'  # 发送广播


def notify_clients(kind, payload, **extra):
    """ 给所有的websocket Client发通知 """
    data = {
        "kind": kind,
    }
    if payload:
        data['payload'] = payload
    if extra:
        data['extra'] = extra
    return redis_client.publish(CH_WEBSOCKET_NOTIFY, json.dumps(data))
