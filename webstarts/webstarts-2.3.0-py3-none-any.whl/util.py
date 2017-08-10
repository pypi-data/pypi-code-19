#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
from functools import wraps
from threading import local

import requests
from structlog import get_logger

from . import defaults, log_id

__author__ = "john"
__all__ = ['req_session']

log = get_logger(__name__)


class Local(local):
  def __init__(self):
    super().__init__()
    self.cache = {}


_local = Local()
_key = requests.Session


def req_session() -> requests.Session:
  """Thread local request sessions"""

  s = _local.cache.get(_key)

  if s is None:
    s = _local.cache[_key] = _key()
    ws = getattr(s.prepare_request, '_webstarts', None)
    log.debug(f'Creating session', ws=ws)
    if ws is None:
      s.prepare_request = pre_hook(s.prepare_request)

  return s


def wrap_session(app):
  """Add req_session as middleware"""

  session = req_session()

  def wrap_session_(environ, start_response):
    environ.update(requests=session)
    return app(environ, start_response)

  return wrap_session_


def pre_hook(f):
  @wraps(f)
  def prepare_request(*args):
    prepared = f(*args)
    if defaults.LOG_KEY not in prepared.headers:
      prepared.headers[defaults.LOG_KEY] = log_id.find()
    return prepared

  prepare_request._webstarts = True
  return prepare_request
