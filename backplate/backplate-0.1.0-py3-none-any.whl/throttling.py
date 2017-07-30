
import math
from datetime import datetime
from functools import wraps
from flask import abort, g

class Throttle(object):

    def __init__(self, hits=None, last=None, obj={}):
        self.hits = obj.get('hits', hits)
        self.last = obj.get('last', last)

    def hit(self):
        self.hits += 1

    def update(self, rate):
        now = datetime.utcnow()
        diff = math.floor((now - self.last).total_seconds())
        hitdiff = math.floor(diff * rate)

        self.last = now
        if self.hits - hitdiff >= 0:
            self.hits -= hitdiff
        else:
            self.hits = 0

    def check(self, capacity):
        return self.hits < capacity

    def dump(self):
        return {
            'hits': self.hits,
            'last': self.last
        }


class ThrottlerBase(object):

    def __init__(self, capacity=None, timeframe=None):
        if type(capacity) is not int:
            raise ValueError("Parameter 'capacity' must be an 'int'.")
        if type(timeframe) is not int:
            raise ValueError("Parameter 'timeframe' must be an 'int'.")

        self.capacity = capacity
        self.timeframe = timeframe
        self.rate = capacity / timeframe

    # Override Methods

    def get_throttle(self, id):
        # should read/create throttle from database
        # return dict
        raise NotImplementedError

    def set_throttle(self, id, throttle):
        # should save throttle in database
        # return None
        raise NotImplementedError

    # Optional Event Methods

    def resolve_user_id(self):
        return g.user.id

    def on_throttle_normal(self, id):
        # optionally bind actions
        # return None
        pass

    def on_throttle_exceed(self, id):
        # optionally bind actions
        # return None
        pass

    # Core Methods

    def request(self, id=None, hit=True):
        if not id:
            return

        thr = self.get_throttle(id)
        thr.update(self.rate)

        # check if throttle has not exceeded
        if thr.check(self.capacity):

            # optionally incrememt hits and save
            if hit:
                thr.hit()
                self.set_throttle(id, thr)

            # trigger throttle normal events
            self.on_throttle_normal(id)
            return True

        # trigger throttle exceed events
        self.on_throttle_exceed(id)
        return False


def create_throttler_decorator(Throttler):

    throttler = Throttler

    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = throttler.resolve_user_id()
            if throttler.request(id=user_id):
                return f(*args, **kwargs)
            return abort(429) # Too Many Requests

        return wrapped
    return wrapper

__all__ = ['Throttle', 'ThrottlerBase', 'create_throttler_decorator']
