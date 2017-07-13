#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import uuid

from structlog import get_logger

from . import defaults, trace

__author__ = "john"

logger = get_logger(__name__)


def err(v):
  ass = 1 + v
  return ass


def make():
  return str(uuid.uuid4())[:12].replace('-', '')


def ctx():
  return dict(logger._context._dict)


def find():
  return ctx().get(defaults.LOG_KEY)


def wrap_logid(app):
  @trace
  def wrap_logid_(environ, start_response):
    # maybe do not need to do .new if logid exists. in backend too.
    logid = environ.get(defaults.LOG_KEY, make())
    environ[defaults.LOG_KEY] = logid
    logger.new(logid=logid)

    @trace
    def wrap_logid_header(status, headers, exc_info=None):
      headers.append((defaults.LOG_KEY, logid))
      start_response(status, headers, exc_info)
    return app(environ, wrap_logid_header)
    # return ClosingIterator(app(environ, wrap_logid_header), lambda: None)
  return wrap_logid_
