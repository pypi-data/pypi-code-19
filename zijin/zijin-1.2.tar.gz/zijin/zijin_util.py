#!/usr/bin/env python
# encoding: utf-8

import contextlib
import signal

from zijin_config import STRATEGY_TIMEOUT


def handle_timeout(sig, frame):
    raise Exception('timeout exception, runtime more than {:d}'.format(STRATEGY_TIMEOUT))


@contextlib.contextmanager
def timeout(seconds):
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(seconds)
    yield


def error_decorator(func):
    def wrapper(*args, **kargs):
        if func.__name__ in ['on_newday', 'on_init']:
            return func(*args, **kargs)
        with timeout(STRATEGY_TIMEOUT):
            return func(*args, **kargs)
    return wrapper


def datetime2str(_datetime):
    return _datetime.strftime('%Y-%m-%d %H:%M:%S')


def date2str(_date):
    return _date.strftime('%Y-%m-%d')

