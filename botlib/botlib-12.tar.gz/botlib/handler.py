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
        self.launch(self.scheduler, daemon=True)
        super().start(*args, **kwargs)
        self._connected.ready()

    def stop(self):
        """ stop the handler. """
        self._state.status = ""
        self._queue.put_nowait(None)
