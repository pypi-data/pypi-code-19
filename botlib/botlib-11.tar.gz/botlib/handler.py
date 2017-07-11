# botlib/scheduler.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

""" schedule events. """

from .launcher import Launcher
from .object import Object
from .register import Register

import logging
import queue
import time

class Handler(Launcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thrs = []
        self._connected = Object()
        self._handlers = Register()
        self._queue = queue.Queue()
        self._running = False
        self._time.start = time.time()

    def callcb(self, event):
        pass

    def dispatch(self, event):
        event.parse()
        for handler in self._handlers.get(event._parsed.cmnd, []):
            logging.info("! handler %s" % str(handler))
            handler(event)

    def scheduler(self, timeout=None):
        self._connected.wait()
        self._running = True
        self._state.status = "running"
        self._time.latest = time.time()
        while self._state.status:
            event = self._queue.get(timeout=timeout)
            if not event:
                break
            self._counter.events = self._counter.events + 1
            self.handle(event)

    def handle(self, event):
        if event and "txt" in event:
            return self.launch(self.dispatch, event)
            
    def prompt(self, *args, **kwargs):
        """ virtual handler to display a prompt. """
        pass

    def put(self, *args, **kwargs):
        """ put an event to the handler. """
        self._queue.put_nowait(*args, **kwargs)

    def register(self, key, value, force=True):
        """ register a handler. """
        self._handlers.register(key, value, force=True)

    def start(self, *args, **kwargs):
        """ give the start signal. """
        from .space import cfg
        logging.info("! start %s" % self.id())
        self.launch(self.scheduler, daemon=True)
        super().start(*args, **kwargs)
        self._connected.ready()

    def stop(self):
        """ stop the handler. """
        self._state.status = ""
        self._queue.put_nowait(None)
