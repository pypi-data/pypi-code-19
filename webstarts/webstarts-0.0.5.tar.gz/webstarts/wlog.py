#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""

import logging
import sys
from typing import Any, Dict

from kids.cache import cache
from structlog import configure_once, processors, stdlib, threadlocal

from . import defaults, types

__author__ = "john"


def setup(conf: Dict[str, Any]):
  """Setup logging first so nothing shits on it

  - Checkout
  """
  logging.setLoggerClass(types.WebstartsLogger)
  logging.getLogger().setLevel(logging.NOTSET)
  set_record_factory()

  formatter = get_formatter(conf)
  handler = get_handler()
  set_handler(logging.DEBUG, handler, formatter)

  setup_struct()
  shush_loggers()

  logger = logging.getLogger(__name__)
  logger.info('Configured Logging')

  from .wflask import sentry_handler
  set_handler(logging.ERROR, sentry_handler(), formatter)


@cache(key=defaults.CACHE_KEY)
def get_formatter(conf: Dict[str, str] = None) -> types.WebstartsFormatter:
  conf = conf or {}
  fmt, proc = conf.get('fmt', None), None
  if conf['debug']:
    formatter = types.DevFormatter(fmt=fmt or defaults.FORMAT_DEBUG, proc=types.DevRenderer())
  else:
    formatter = types.WebstartsFormatter(fmt=fmt or defaults.FORMAT, proc=types.ExtrasProcessor())
  return formatter


def set_handler(level: int, handler: logging.Handler, formatter: logging.Formatter = None) -> None:
  if formatter:
    handler.setFormatter(formatter)
  handler.setLevel(level)
  logging.getLogger().addHandler(handler)


def setup_struct() -> None:
  """Configure the shit"""
  configure_once(
    processors=[
      stdlib.filter_by_level,
      stdlib.PositionalArgumentsFormatter(),
      processors.UnicodeDecoder(),
      render_to_log_kwargs,
    ],
    context_class=threadlocal.wrap_dict(dict),
    logger_factory=types.LogFactory(),
    wrapper_class=stdlib.BoundLogger,
    cache_logger_on_first_use=True,
  )


@cache(key=defaults.CACHE_KEY)
def get_handler() -> logging.StreamHandler:
  return logging.StreamHandler(sys.stdout)


def set_record_factory() -> None:
  old_factory = logging.getLogRecordFactory()
  # noinspection PyMissingTypeHints
  def record_factory(*args, **kwargs):
    from webstarts import log_id
    record = old_factory(*args, **kwargs)
    record.logid = log_id.find()
    record.extras = ''
    return record
  logging.setLogRecordFactory(record_factory)


def render_to_log_kwargs(_, __, event_dict) -> Dict:
  extra = event_dict.pop('extra', {})
  exc = event_dict.pop('exc_info', None)
  stack_info = event_dict.pop('stack_info', False)
  event_dict.pop('logid', None)
  ret = dict(msg=event_dict.pop("event", ''), extra={'ed': event_dict, **extra}, exc_info=exc, stack_info=stack_info)
  return ret


def shush_loggers():
  names = [
    'passlib'
  ]
  for n in names:
    logging.getLogger(n).setLevel(logging.WARN)
