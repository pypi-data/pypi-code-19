#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""

import logging

from celery import signals
from kids.cache import cache
from raven.contrib.celery import CeleryFilter, SentryCeleryHandler
from structlog import get_logger

from . import defaults, log_id, trace, wflask

__author__ = "john"

logger = get_logger(__name__)


def setup_celery(_):
  """Register celery shit"""

  signals.setup_logging.connect(on_setup)
  signals.before_task_publish.connect(on_before_pub)
  signals.task_prerun.connect(on_prerun)
  get_sentry_handler().install()
  add_celery_filter()

  logger.info('Configured Celery')
  set_logs_to_info()


def on_setup(**_):
  pass


@cache(key=defaults.CACHE_KEY)
def get_sentry_handler():
  return SentryCeleryHandler(wflask.get_client())


def add_celery_filter():
  handler = wflask.sentry_handler()
  if not [f for f in handler.filters if isinstance(f, CeleryFilter)]:
    handler.addFilter(CeleryFilter())


@trace
def on_before_pub(headers=None, **_):
  headers[defaults.LOG_KEY] = log_id.find()


@trace
def on_prerun(task_id=None, task=None, **_):
  logid = getattr(task.request, 'logid', None)
  # ctx = dict(tid=task_id, task=task.name, logid=logid)
  ctx = dict(logid=logid)
  logger.new(**ctx)


def set_logs_to_info():
  names = [
    'amqp',
    'kombu',
    'celery'
  ]
  [logging.getLogger(n).setLevel(logging.INFO) for n in names]
