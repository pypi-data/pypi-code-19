import json
from urllib.parse import urlparse

import redis
from django.conf import settings

backend_conf = urlparse(settings.WS4EVER['BROADCAST_BACKEND'])
redis_client = redis.StrictRedis(backend_conf.hostname, password=backend_conf.password, decode_responses=True, db=0)
CH_WEBSOCKET_NOTIFY = 'websocket:notify'  # 发送广播


def publish_client_message(kind, payload, **extra):
    data = {
        "kind": kind,
        "payload": payload,
        **extra
    }
    return redis_client.publish(CH_WEBSOCKET_NOTIFY, json.dumps(data))
