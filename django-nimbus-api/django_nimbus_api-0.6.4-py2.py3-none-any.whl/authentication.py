"""
Provides various authentication policies.
"""
from __future__ import unicode_literals

import json
import base64
import binascii
import hashlib
import urllib
import logging

from django.conf import settings
from django.utils import six
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.timezone import datetime, timedelta, now, is_aware, is_naive
from django.http import QueryDict
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.exceptions import APIException
from rest_framework import status

from . import utils

logger = logging.getLogger(__name__)


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Incorrect authentication credentials.'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class TokenSignAuthentication(BaseAuthentication):
    expiry_minutes = 5
    auth_params = [
        "token", "username", "platform", "deviceid", "timestamp", "sign",
    ]
    sign_params = [
       "method", "scheme", "uri",  "username", "platform", "deviceid", "token", "timestamp", "version",
    ]
    sign_prefix = u"SDCP"
    sign_param = "sign"
    timestamp_param = "timestamp"

    def authenticate(self, request):
        kwargs = {key: utils.get_header(request, key, "") for key in self.auth_params}
        version = request.version
        func = getattr(self, "authenticate_{}".format(version), None)
        if func and callable(func):
            return func(request=request, version=version, **kwargs)
        raise AuthenticationFailed(_('Authentication Failed'))

    def authenticate_token(self, request, **kwargs):
        """
        :param request:
        :param kwargs:
        :return: (user, token) tuple
        """
        raise NotImplementedError(".authenticate_token() must be overridden.")

    def authenticate_sign(self, request, **kwargs):
        sign = kwargs.get(self.sign_param, None)
        if not sign:
            raise AuthenticationFailed(_('Invalid sign.'))
        method = request.method
        scheme = request.scheme
        uri = request.path
        newsign = self.get_sign(request, method=method.lower(), scheme=scheme, uri=uri, **kwargs)
        if not newsign or newsign != sign:
            raise AuthenticationFailed(_('Invalid sign.'))

    def authenticate_timestamp(self, **kwargs):
        timestamp = kwargs.get(self.timestamp_param, None)
        if not timestamp:
            raise AuthenticationFailed(_('Invalid timestamp.'))
        dt = utils.to_datetime(timestamp)
        n = now()
        delta = n - dt if n > dt else dt - n
        if delta > timedelta(minutes=self.expiry_minutes):
            raise AuthenticationFailed(_('Invalid timestamp.'))

    def authenticate_v1(self, request, **kwargs):
        user, token = self.authenticate_token(request, **kwargs)
        return (user, token)

    def authenticate_v2(self, request, **kwargs):
        user, token = self.authenticate_token(request, **kwargs)
        self.authenticate_sign(request, **kwargs)
        return (user, token)

    def authenticate_v3(self, request, **kwargs):
        user, token = self.authenticate_token(request, **kwargs)
        self.authenticate_sign(request, **kwargs)
        self.authenticate_timestamp(**kwargs)
        return (user, token)

    def get_sign(self, request, **kwargs):
        unsign_value = u"|".join([u"{}".format(kwargs.get(p, "")) for p in self.sign_params])
        unsign = u"{}|{}".format(self.sign_prefix, unsign_value)
        return hashlib.md5(unsign).hexdigest()
