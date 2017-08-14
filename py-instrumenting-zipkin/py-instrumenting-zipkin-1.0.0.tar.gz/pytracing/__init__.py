from __future__ import absolute_import

import threading
import sys


def merge_dicts(*dicts):
    out = {}
    for d in dicts:
        if not d:
            continue

        for k, v in iteritems(d):
            out[k] = v
    return out


class memoize(object):
    """
    Memoize the result of a property call.

    >>> class A(object):
    >>>     @memoize
    >>>     def func(self):
    >>>         return 'foo'
    """

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        d, n = vars(obj), self.__name__
        if n not in d:
            d[n] = self.func(obj)
        return d[n]


def once(func):
    """
    Runs a thing once and once only.
    """
    lock = threading.Lock()

    def new_func(*args, **kwargs):
        if new_func.called:
            return
        with lock:
            if new_func.called:
                return
            rv = func(*args, **kwargs)
            new_func.called = True
            return rv

    new_func = update_wrapper(new_func, func)
    new_func.called = False
    return new_func


from .apitracer import request_tracer as zipkin_tracer
