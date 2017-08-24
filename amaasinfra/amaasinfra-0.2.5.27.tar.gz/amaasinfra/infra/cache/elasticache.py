import redis

class Cache(object):
    def __init__(self, server='localhost', port=6379, db=0):
        redis_db = redis.StrictRedis(host=server, port=port, db=db)

    def set(self, key, value):
        raise NotImplementedError()

    def get(self, key):
        raise NotImplementedError()


class Redis(Cache):
    def __init__(self):
        super().__init__()

    def set(self, key, value):
        pass

    def get(self, key):
        pass