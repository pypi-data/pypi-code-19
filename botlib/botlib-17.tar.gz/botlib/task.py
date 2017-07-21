# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready = threading.Event()
        self._func = args[1]
        self._name = args[2]
        try:
            self._event = args[3]
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

    def isSet(self):
        """ see if the object ready flag is set. """
        return self._ready.isSet()

    def ready(self):
        """ signal the event as being ready. """
        self._ready.set()

    def clear(self):
        """ clear the ready flag. """
        self._ready.clear()

    def wait(self, sec=180.0):
        """ wait for the task to be ready. """
        self._ready.wait()
