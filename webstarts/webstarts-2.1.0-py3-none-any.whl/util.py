#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
from functools import wraps
from multiprocessing import current_process
from threading import current_thread, local

import requests
from structlog import get_logger

from . import defaults, log_id

__author__ = "john"
__all__ = ['req_session']


class Local(local):
  def __init__(self):
    super().__init__()
    self.cache = {}


_local = Local()
_key = requests.Session

log = get_logger(__name__)


def req_session() -> requests.Session:
  """Thread local request sessions"""

  thread = current_thread().name
  proc = current_process().name
  s = _local.cache.get(_key)

  if s is None:
    s = _local.cache[_key] = _key()
    ws = getattr(s.prepare_request, '_webstarts', None)
    log.info(f'Creating session', ws=ws, thread=thread, proc=proc)
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
    # log.info('Hooking session', cunt=prepare_request._webstarts, thread=thread, proc=proc)
    if defaults.LOG_KEY not in prepared.headers:
      prepared.headers[defaults.LOG_KEY] = log_id.find()
    return prepared

  prepare_request._webstarts = True
  return prepare_request
