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
from .utils import get_keyword, get_authorization_header
from .rsa_encrpy import RSAEncryption

logger = logging.getLogger(__name__)


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        try:
            token = get_keyword(request, self.keyword)
            logger.debug("[authentication] token:%s", token)
            if not token:
                raise exceptions.APIException()
        except Exception:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        pass


class RSATokenAuthentication(BaseAuthentication):
    AUTH_RSA = False
    AUTH_SIGN = True

    API_PRIVATE_KEY = "API_PRIVATE_KEY"
    API_SECRECT_KEY = "API_SECRECT_KEY"

    PARAM_KEY = 'key'
    PARAM_SIGN = 'sign'
    PARAM_TOKEN = 'token'
    EXCLUDES = ['sign', ]
    INCLUDES = []
    EXPIRATION = 0

    model = None

    def __init__(self):
        super(RSATokenAuthentication, self).__init__()
        self.encrpy = RSAEncryption()

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def authenticate(self, request):
        logger.debug("[authentication] id:%s", id(self))
        self.authenticate_rsa(request)
        self.authenticate_sign(request)
        token = self.get_token(request)
        return self.authenticate_credentials(token)

    def authenticate_header(self, request):
        pass

    @property
    def private_key(self):
        if not hasattr(self, "_private_key"):
            self._private_key = getattr(settings, self.API_PRIVATE_KEY, None)
        return self._private_key

    @property
    def secrect_key(self):
        if not hasattr(self, "_secrect_key"):
            self._secrect_key = getattr(settings, self.API_SECRECT_KEY, None)
        return self._secrect_key

    def authenticate_rsa(self, request):
        try:
            key = get_keyword(request, self.PARAM_KEY)
            if not self.AUTH_RSA:
                return key or True
            if not key:
                raise exceptions.AuthenticationFailed(_('Invalid key.'))
            if request.method == 'POST':
                _rawdata = self.encrpy.decrypt(key, self.private_key)
                request.POST = QueryDict()
                request.POST.update(json.loads(_rawdata))
                return True
            elif request.method == 'GET' and settings.DEBUG:
                _rawdata = self.encrpy.decrypt(key, self.private_key)
                request.GET = QueryDict()
                request.GET.update(json.loads(_rawdata))
                return True
            else:
                raise exceptions.AuthenticationFailed(_('Invalid key.'))
        except Exception:
            raise exceptions.AuthenticationFailed(_('Invalid key.'))

    def authenticate_sign(self, request):
        try:
            sign = get_keyword(request, self.PARAM_SIGN)
            if not self.AUTH_SIGN:
                return sign or True
            if not sign:
                raise exceptions.AuthenticationFailed(_('Invalid sign.'))
            _sign = self.gen_sign(request)
            if not _sign:
                raise exceptions.AuthenticationFailed(_('Invalid sign.'))
            if _sign != sign:
                raise exceptions.AuthenticationFailed(_('Invalid sign.'))
            return sign
        except Exception:
            raise exceptions.AuthenticationFailed(_('Invalid sign.'))

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            if not key:
                raise exceptions.AuthenticationFailed(_('Invalid token.'))
            if self.EXPIRATION > 0:
                _now = now() - timedelta(hours=self.EXPIRATION)
                token = model.objects.select_related('user').filter(created__gte=_now).get(key=key)
            else:
                token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user, token

    def get_token(self, request):
        token = get_keyword(request, self.PARAM_TOKEN)
        return token

    def gen_sign(self, request):
        params = request.GET if request.GET else request.POST
        params = params.dict()
        keys = params.keys()
        keys.sort()

        gather = request.method
        if self.INCLUDES and self.EXCLUDES:
            gather += u"&".join(["{key}={value}".format(
                key=k, value=params.get(k)) for k in keys if (k in self.INCLUDES) and (k not in self.EXCLUDES)])
        elif self.INCLUDES:
            gather += u"&".join(["{key}={value}".format(
                key=k, value=params.get(k)) for k in keys if (k in self.INCLUDES)])
        elif self.EXCLUDES:
            gather += u"&".join(["{key}={value}".format(
                key=k, value=params.get(k)) for k in keys if (k not in self.EXCLUDES)])
        else:
            gather += u"&".join(["{key}={value}".format(
                key=k, value=params.get(k)) for k in keys])
        if self.secrect_key:
            gather += self.secrect_key
        logger.debug("[sign] before: %s", gather)
        sign = hashlib.md5(urllib.quote_plus(gather))
        h = sign.hexdigest()
        logger.debug("[sign] after: %s", h)
        return h
