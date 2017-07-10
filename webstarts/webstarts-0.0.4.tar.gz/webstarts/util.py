#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import threading

import requests
from decorator import decorator

from . import defaults, log_id

__author__ = "john"
__all__ = ['req_session']

_local = threading.local()
_local.cache = {}
_key = requests.Session


def req_session() -> requests.Session:
  """Thread local request sessions"""
  if _key not in _local.cache:
    _key.prepare_request = _pre_hook(_key.prepare_request)
  _local.cache[_key] = _local.cache.get(_key, _key())
  return _local.cache[_key]


@decorator
def _pre_hook(f, *args):
  prepared = f(*args)
  if defaults.LOG_KEY not in prepared.headers:
    prepared.headers[defaults.LOG_KEY] = log_id.find()
  return prepared
