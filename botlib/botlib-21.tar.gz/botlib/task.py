# BOTLIB Framework to program bots
#
# botlib/task.py
#
# Copyright 2017 B.H.J Thate
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" adapted thread to add extra functionality to threads. """

from .object import Default, Object
from .event import Event
from .trace import get_exception
from .utils import name

import logging
import queue
import threading
import time

class Task(threading.Thread):

    """ Task are adapted Threads. """

    def __init__(self, group, target, name, args, kwargs, *, daemon=True):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self._ready = threading.Event()
        self._func = target
        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._result = 0
        try:
            self._event = args[0]
        except:
            self._event = Event()
        try:
            self._self = self._func.__self__
            self._state = self._self._state
            self._counter = self._self._counter
            self._error = self._self._error
            self._status = self._self._status
        except:
            self._self = None
            self._state = Object()
            self._counter = Default(default=0)
            self._error = Object()
            self._status = Object()
        try:
            self._event = args[3]
            self._name = self._event._parsed.cmnd
        except:
            self._event = Event()
        self._time = Default(default=0)
        self._time.start = time.time()
        self.setName(self._name)

    def __iter__(self):
        """ return self as an iterator. """
        return self

    def __next__(self):
        """ yield next value. """
        for k in dir(self):
            yield k

    def run(self):
        try:
            self._result = self._func(*self._args, **self._kwargs)
        except Exception as ex:
            logging.error(get_exception())
        return self._result or 0

    def isSet(self):
        """ see if the object ready flag is set. """
        return self._ready.isSet()

    def join(self, sleep=10.0):
        """ join this task and return the result. """
        super().join(sleep)
        self.ready()
        return self._result

    def ready(self):
        """ signal the event as being ready. """
        self._ready.set()

    def clear(self):
        """ clear the ready flag. """
        self._ready.clear()

    def wait(self, sec=180.0):
        """ wait for the task to be ready. """
        self._ready.wait()
        return self._result
