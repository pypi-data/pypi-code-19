import redis
from django.conf import settings

redis_client = redis.StrictRedis(settings.REDIS_HOST, password=settings.REDIS_PASSWORD, decode_responses=True, db=0)
CH_WEBSOCKET_NOTIFY = 'websocket:notify'  # 发送广播


def remove_empty_keys(d):
    for k, v in list(d.items()):
        if v is None:
            del d[k]

# when you need to publish message, you can
# rc_main.publish(CH_WEBSOCKET_NOTIFY, json.dumps({'kind':'','payload':''}))
