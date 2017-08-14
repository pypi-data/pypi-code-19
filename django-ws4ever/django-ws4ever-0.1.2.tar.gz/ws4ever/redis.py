import json
from typing import Any, Optional

import redis
from django.conf import settings

redis_client = redis.StrictRedis(settings.WS4EVER['BROADCAST_BACKEND']['REDIS_HOST'],
                                 password=settings.WS4EVER['BROADCAST_BACKEND']['REDIS_HOST'],
                                 decode_responses=True, db=0)
CH_WEBSOCKET_NOTIFY = 'websocket:notify'  # 发送广播


def remove_empty_keys(d):
    for k, v in list(d.items()):
        if v is None:
            del d[k]


def publish_client_message(kind: str, payload: Optional[Any]):
    if isinstance(msg, str):
        msg = {'kind': msg}

    remove_empty_keys(msg)

    if msg.get('kind'):
        return redis_client.publish(CH_WEBSOCKET_NOTIFY, json.dumps(msg))
