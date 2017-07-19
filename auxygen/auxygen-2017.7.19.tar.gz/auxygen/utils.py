#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime


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


def customable(func):
    def wrapper(*args, **kwargs):
        scope = sys._getframe().f_back.f_code.co_name
        if scope != '<module>':
            kwargs['now'] = True
        return func(*args, **kwargs)
    return wrapper


def calcTime(uptime):
    delta = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=uptime)
    return delta.day - 1, delta.hour, delta.minute


def pyqt2bool(entry):
    return not (entry == 'false' or not entry)
