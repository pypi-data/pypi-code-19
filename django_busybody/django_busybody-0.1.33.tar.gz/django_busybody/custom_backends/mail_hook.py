# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured


class MailBackendHook(object):
    def __init__(self, *args, **kwarg):
        upstream = getattr(settings, 'EMAIL_BACKEND_UPSTREAM')
        if not upstream:  # pragma: no cover
            raise ImproperlyConfigured('EMAIL_BACKEND_UPSTREAM must be set')
        self.__dict__['_upper_'] = import_string(upstream)(*args, **kwarg)

    def __getattr__(self, key):
        return getattr(self.__dict__['_upper_'], key)

    def __setattr__(self, key, value):
        return setattr(self.__dict__['_upper_'], key, value)
