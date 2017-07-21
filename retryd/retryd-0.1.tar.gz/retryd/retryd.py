#! /usr/bin/python3
# -*- coding: utf-8 -*-
from functools import wraps
import logging
import time


def try_except_pass(errors=(Exception, )):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                return e
        return wrapper
    return decorate


def try_redo(times=3, delay=3):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ans = None
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # do something, eg: delay some thime
                    time.sleep(delay)
                    ans = e
            raise ans

        return wrapper
    return decorate


def failed_todo(function, message, *args, **kwargs):
    a = args
    k = kwargs
    def decorate(func):
        module = func.__module__
        name = func.__name__
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return function(message, module, name, e, *a, **k)
        return wrapper
    return decorate
