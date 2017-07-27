#!/usr/bin/env python
# -*- coding: utf-8 -*-


DEFAULT_TIMEOUT = 3000
DEFAULT_ERROR = 0.5


def split_motor_name(func):
    def wrapper(*args, **kwargs):
        if len(args) >= 1:
            args = list(args)
            if isinstance(args[1], str) and '->' in args[1]:
                args[1] = args[1].split('->')[-1]
        return func(*args, **kwargs)
    return wrapper


def calcTime(uptime):
    m, s = divmod(int(uptime), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return d, h, m


def pyqt2bool(entry):
    return not (entry == 'false' or not entry)
