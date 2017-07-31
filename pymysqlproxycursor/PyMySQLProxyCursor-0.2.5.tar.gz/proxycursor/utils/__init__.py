# -*- coding: utf-8 -*-

import six

from . import parser


def get_bound_method(obj, method_name):
    method = getattr(obj, method_name, None)
    if method is not None:
        if six.get_method_self(method) is None:
            msg = '{0} must be a bound method'.format(method)
            raise AttributeError(msg)
    return method

