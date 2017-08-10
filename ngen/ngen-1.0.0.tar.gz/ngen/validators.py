"""
"""
from __future__ import absolute_import, print_function, unicode_literals

import datetime
import numbers

import six

from .exceptions import ValidationError
from future.utils import raise_with_traceback


def check_length(value, min_length=None, max_length=None):
    if min_length and len(value) < min_length:
        raise ValidationError(
            '{} is too short. Min length is {}'.format(value, min_length)
        )
    if max_length and len(value) > max_length:
        raise ValidationError(
            '{} is too long. Max length is {}'.format(value, max_length)
        )
    return value


def is_datetime(value):
    if not isinstance(value, datetime.datetime):
        raise ValidationError('Expected a datetime object.')
    return value


def is_date(value):
    if not isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
        raise ValidationError('Expected a date object.')
    return value


def is_bool(value):
    if not isinstance(value, bool):
        raise ValidationError('Expected a bool object.')
    return value


def is_set(value):
    if not isinstance(value, set):
        raise ValidationError('Expected a set object.')
    return value


def is_dict(value):
    if not isinstance(value, dict):
        raise ValidationError('Expected a dict object.')
    return value


def is_list(value):
    if not isinstance(value, (list, tuple)):
        raise ValidationError('Expected a list or tuple object.')
    return value


def is_int(value):
    msg = 'Expected an int object.'
    if isinstance(value, six.string_types) and not value.isdigit():
        raise ValidationError(msg)
    elif not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(msg)
    return value


def is_float(value):
    if not isinstance(value, float):
        raise ValidationError('Expected a float object.')
    return value


def is_number(value):
    if not isinstance(value, numbers.Number) or isinstance(value, bool):
        raise ValidationError(
            '{}, must be a number.'.format(value)
        )
    return value


def is_char(value):
    if not isinstance(value, six.string_types):
        raise ValidationError('Expected a char object.')
    return value
