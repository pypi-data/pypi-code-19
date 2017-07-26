# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from . import middlewares


def get_global_request(attr=None):
    th_local = middlewares.GlobalRequestMiddleware.thread_local
    if hasattr(th_local, 'request'):
        if attr:
            return getattr(th_local.request, attr, None)
        return th_local.request
    return None
