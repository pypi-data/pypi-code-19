# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
Package Description
"""
import os
import sys
import logging
import json
from functools import wraps
from importlib import import_module
from django.utils.six import text_type
from rest_framework import HTTP_HEADER_ENCODING, exceptions


def import_module_attr(path):
    package, module = path.rsplit('.', 1)
    return getattr(import_module(package), module)


def format_exception(status_code, detail):
    data = {
        "code": status_code,
        "msg": detail
    }
    return data


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


def get_keyword(request, keyword):
    token = request.GET.get(keyword, None)
    return token or request.POST.get(keyword, None)
