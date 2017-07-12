# BOTLIB - Framework to program bots.
#
# Copyright (C) 2016,2017 by Bart Thate <bthate@dds.nl>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE 
# FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY 
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

""" adapted thread to add extra functionality to threads. """

from .event import Event
from .object import Default, Object
from .trace import get_exception
from .utils import name, sname

import logging
import multiprocessing
import threading
import time
import queue

class Task(threading.Thread):

    """ Task are adapted Threads. """

    _counter = Default(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDaemon(kwargs.get("daemon", False))
        self._error = Default(default="")
        self._counter = Default(default=0)
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._result = Object()
        self._running = False
        self._state = Default()
        self._time = Default(default=0)
        self.args = args
        self.kwargs = kwargs
        self.once = False

    def __iter__(self):
        """ return self as an iterator. """
        return self
        
    def __next__(self):
        """ yield next value. """
        for k in dir(self):
            yield k

    def put(self, func, *args):
        """ put a new function to execute. """
        if not self._running:
            self._running = True
            self.start()
        if args:
            self._event = args[0]
            try:
                self._name = self._event._parsed.txt or self.kwargs.get("name", name(func))
            except AttributeError:
                self._name = self.kwargs.get("name", name(func))
        else:
            self._event = None
            self._name = self.kwargs.get("name", name(func))
        self.setName(self._name)
        self._queue.put_nowait((func, args))
        return self

    def run(self):
        """ run the threads botloop. """
        self._time.start = time.time()
        _func, args = self._queue.get()
        self._result= Object()
        self._state.status = "running"
        if self.args:
            self._event = args[0]
            self._state.origin = self._event.origin
            logging.debug(self._event)
        self._time.latest = time.time()
        try:
            self._result = _func(*args)
        except:
            logging.error(get_exception())
        try:
            args[0].ready()
        except:
            pass
        self._state.status = "stopped"
        return self._result

    def stop(self):
        """ stop the task. """
        self._state.status = ""
        self.put(None, None)

    def join(self, *args, **kwargs):
        """ join the thread and signal ready. """
        super().join()
        #self.ready()
        return self._result

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
