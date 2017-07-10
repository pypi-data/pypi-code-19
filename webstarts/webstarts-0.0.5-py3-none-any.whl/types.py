#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import logging
from io import StringIO

import colorama
from structlog import stdlib
from structlog.processors import KeyValueRenderer
from structlog.stdlib import _FixedFindCallerLogger

__author__ = "john"


class LogFactory(stdlib.LoggerFactory):
  """LoggerFactory for structlog"""

  def __init__(self, ignore_frame_names=None):
    super().__init__(ignore_frame_names=ignore_frame_names)
    logging.setLoggerClass(WebstartsLogger)


class WebstartsLogger(_FixedFindCallerLogger):
  """Root logger who will handle end result from structlog"""

  def _log(self, level, msg, *args, **kwargs):
    super()._log(level, msg, *args, **kwargs)

  def makeRecord(self, *args, **kwargs):
    return super().makeRecord(*args, **kwargs)


class WebstartsFormatter(logging.Formatter):
  """End logging formatter for all"""

  def __init__(self, fmt=None, proc=None, **kwargs):
    self.proc = proc
    super().__init__(fmt, **kwargs)

  def format(self, record):
    if self.proc:
      record.extras = self.proc.run(record)
    record.msg = f'"{record.msg}"'
    return super().format(record)


class ExtrasProcessor(KeyValueRenderer):
  """Replace ConsoleRenderer for final output """

  def run(self, record):
    ed = record.__dict__.get('ed', {})
    return ' '.join(k + '=' + self._repr(v) for k, v in self._ordered_items(ed))


class DevFormatter(logging.Formatter):
  """End logging formatter for all"""

  def __init__(self, proc=None, **kwargs):
    kwargs.pop('fmt', None)
    self.proc = proc
    super().__init__(fmt='%(message)s', **kwargs)

  def format(self, record):
    if self.proc:
      record.msg = self.proc.run(record)
    return super().format(record)


reset = colorama.Style.RESET_ALL
bright = colorama.Style.BRIGHT
dim = colorama.Style.DIM
red = colorama.Fore.RED
blue = colorama.Fore.BLUE
cyan = colorama.Fore.CYAN
magenta = colorama.Fore.MAGENTA
yellow = colorama.Fore.YELLOW
green = colorama.Fore.GREEN
rb = colorama.Back.RED
brblack = colorama.Fore.BLACK + bright


class DevRenderer(object):
  """Pretty shit"""

  NAME = blue + bright
  KEY = cyan
  VALUE = magenta
  LEVELS = dict(warning=colorama.Fore.LIGHTYELLOW_EX, info=green, debug=blue, notset=rb)
  LEVELS['critical'] = LEVELS['exception'] = LEVELS['error'] = red

  def __init__(self, name_pad=40, msg_pad=100):
    colorama.deinit()
    self.msg_pad = msg_pad
    self.name_pad = name_pad
    keys = self.LEVELS.keys()
    for k in keys:
      self.LEVELS[k] += bright

  def run(self, record):
    sio = StringIO()
    event_dict = record.__dict__.get('ed', {})
    namepad, msgpad, namecol, key, value = self.name_pad, self.msg_pad, self.NAME, self.KEY, self.VALUE
    name = record.name
    level = record.levelname.lower()
    levcol = self.LEVELS[level]
    logid = record.logid or 'None'
    msg = str(record.msg)
    if len(msg) > msgpad:
      msg = msg[:msgpad - 4] + '...'
    msg += '"'

    sio.write(f'[{levcol}{level:8}{reset}] {brblack}{logid:11}{reset} {namecol}{name:{namepad}}{reset} "{msg:{msgpad}}')

    stack = event_dict.pop('stack', None)
    exc = event_dict.pop('exception', None)

    atoms = list(event_dict.items())
    if atoms:
      atoms.sort(key=lambda e: str(e[0]))
      log_atom = ' '.join(f'{key}{k}{reset}{brblack}={reset}{value}{v}{reset}' for k, v in atoms)
      sio.write(f' {log_atom}')

    if stack is not None:
      sio.write("\n" + stack)
      if exc is not None:
        sio.write("\n\n" + "=" * 79 + "\n")
    if exc is not None:
      sio.write("\n" + exc)

    return sio.getvalue()


class StructFormatter(logging.Formatter):
  """End formatter maybe"""

  def __init__(self, processor, foreign_pre_chain=None, keep_exc_info=False, keep_stack_info=False, *args, **kwargs):
    self.processor = processor
    self.foreign_pre_chain = foreign_pre_chain
    self.keep_exc_info = keep_exc_info
    self.keep_stack_info = keep_stack_info
    fmt = kwargs.pop('fmt')
    if isinstance(processor, DevRenderer): fmt = '%(message)s'
    super().__init__(*args, fmt=fmt, **kwargs)

  # @trace
  def format(self, record):
    """Figure out what to do with exc_info"""

    if isinstance(record.msg, dict):
      ed = record.msg.copy()
    else:
      ed = {"event": record.getMessage(), "_record": record}
      record.args = ()
      # if record.exc_info:
      #   ed["exc_info"] = record.exc_info
      # if record.stack_info:
      #   ed["stack_info"] = record.stack_info
      # if not self.keep_exc_info:
      #   record.exc_text = None
      #   record.exc_info = None
      # if not self.keep_stack_info:
      #   record.stack_info = None
      for proc in self.foreign_pre_chain or ():
        ed = proc(None, record.name, ed)
      del ed['_record']
    record.msg = self.processor(record, record.name, ed)

    return super().format(record)
