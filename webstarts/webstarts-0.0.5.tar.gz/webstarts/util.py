#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import threading

import requests
from decorator import decorator

from . import defaults, log_id

__author__ = "john"
__all__ = ['req_session']


class Local(threading.local):
  def __init__(self):
    super().__init__()
    self.cache = {}


_local = Local()
_key = requests.Session


def req_session() -> requests.Session:
  """Thread local request sessions"""

  if _key not in _local.cache:
    _key.prepare_request = _pre_hook(_key.prepare_request)
  _local.cache[_key] = _local.cache.get(_key, _key())
  return _local.cache[_key]


def wrap_session(app):
  """Add req_session as middleware"""

  session = req_session()

  def wrap_session_(environ, start_response):
    environ.update(requests=session)
    return app(environ, start_response)
  return wrap_session_


@decorator
def _pre_hook(f, *args):
  prepared = f(*args)
  if defaults.LOG_KEY not in prepared.headers:
    prepared.headers[defaults.LOG_KEY] = log_id.find()
  return prepared
