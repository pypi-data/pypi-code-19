# -*- coding: utf-8 -*-
import os
"""Top-level package for envir."""

__author__ = """Kilerd Chan"""
__email__ = 'blove694@gmail.com'
__version__ = '0.0.1'

__all__ =('EnvirFormatException', 'STR', 'INT', 'FLOAT', 'BOOL', 'load')


class EnvirFormatException(Exception):

    def __init__(self, value, format):
        self.value = value
        self.format = format

    def __str__(self):
        return 'could not format {} to {} type'.format(self.value, self.format)


def STR(value):
    return value


def INT(value):
    try:
        return int(value)
    except:
        raise EnvirFormatException(value, 'INT')


def FLOAT(value):
    try:
        return float(value)

    except:
        raise EnvirFormatException(value, 'FLOAT')


def BOOL(value):

    if value.upper() == 'TRUE':
        return True
    elif value.upper() == 'FALSE':
        return False
    else:
        raise EnvirFormatException(value, 'BOOL')


def load(variable, format=STR, default=None):

    env_variable = os.environ.get(variable, None)
    if env_variable:
        return format(env_variable)
    else:
        return default
