# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import uuid
import base64
import logging
import collections
from collections import Mapping, OrderedDict
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import MiddlewareNotUsed, PermissionDenied, SuspiciousOperation
from django.conf import settings
from django.utils import six, timezone
from django.contrib import auth
from django.shortcuts import render
from django.dispatch import receiver
from django.db.models import F, Q
from django.db.models import Count, Avg, Sum, Aggregate
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.urls import reverse
from django.shortcuts import resolve_url
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import View, CreateView, ListView, DetailView, UpdateView
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils.safestring import mark_safe, mark_for_escaping
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware, make_naive, is_aware, is_naive, now, utc
from django.utils.encoding import smart_str, smart_unicode, smart_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from rest_framework.compat import is_authenticated, is_anonymous
from rest_framework.compat import JSONField
from rest_framework import exceptions, status
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.fields import get_error_detail, set_value, empty
from rest_framework.compat import set_rollback
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils import formatting
from rest_framework import serializers, viewsets, generics, mixins
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, GenericViewSet, ReadOnlyModelViewSet, ModelViewSet, ViewSetMixin

from . import utils

logger = logging.getLogger(__name__)


class DateTimeFieldWihTZ(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)


class Base64Field(serializers.CharField):
    def to_internal_value(self, data):
        data = base64.urlsafe_b64decode(data)
        return super(Base64Field, self).to_internal_value(data)

    def to_representation(self, value):
        value = base64.urlsafe_b64encode(value)
        return super(Base64Field, self).to_representation(value)


class RSABase64Field(serializers.CharField):
    def get_decrypt_key(self):
        raise NotImplementedError(".get_decrypt_key() must be overridden.")

    def get_encrypt_key(self):
        raise NotImplementedError(".get_encrypt_key() must be overridden.")

    def decrypt_rsa(self, data):
        return utils.decrypt_rsa(data, self.get_decrypt_key())

    def encrypt_rsa(self, value):
        return utils.encrypt_rsa(value, self.get_encrypt_key())

    def to_internal_value(self, data):
        data = base64.urlsafe_b64decode(data)
        data = self.decrypt_rsa(data)
        return super(RSABase64Field, self).to_internal_value(data)

    def to_representation(self, value):
        value = base64.urlsafe_b64encode(value)
        value = self.encrypt_rsa(value)
        return super(RSABase64Field, self).to_representation(value)


class RSABase64MethodField(serializers.SerializerMethodField):
    def get_decrypt_key(self):
        raise NotImplementedError(".get_decrypt_key() must be overridden.")

    def get_encrypt_key(self):
        raise NotImplementedError(".get_encrypt_key() must be overridden.")

    def decrypt_rsa(self, data):
        return utils.decrypt_rsa(data, self.get_decrypt_key())

    def encrypt_rsa(self, value):
        return utils.encrypt_rsa(value, self.get_encrypt_key())

    def to_internal_value(self, data):
        data = base64.urlsafe_b64decode(data)
        data = self.decrypt_rsa(data)
        return super(RSABase64MethodField, self).to_internal_value(data)

    def to_representation(self, value):
        value = base64.urlsafe_b64encode(value)
        value = self.encrypt_rsa(value)
        return super(RSABase64MethodField, self).to_representation(value)


