# BOTLIB - Framework to program bots.
#
# Copyright (C) 2017 by Bart Thate <bthate@dds.nl>
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
from .trace import get_exception

import logging
import queue
import time

launcher = Launcher()

class Handler(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers = Register()
        self._queue = queue.Queue()
        self._running = False
        self._stopped = False
        self._time.start = time.time()

    def handler(self, event):
        for handler in self._handlers.get(event._parsed.cmnd, []):
            handler(event)

    def scheduler(self, timeout=None):
        self._state.status = "running"
        self._time.latest = time.time()
        while not self._stopped:
            event = self._queue.get(timeout=timeout)
            self._counter.events = self._counter.events + 1
            try:
                self.handler(event)
            except:
                logging.error(get_exception())

    def prompt(self, *args, **kwargs):
        """ virtual handler to display a prompt. """
        pass

    def put(self, *args, **kwargs):
        """ put an event to the handler. """
        self._queue.put(*args, **kwargs)

    def register(self, key, value, force=False):
        """ register a handler. """
        self._handlers.register(key, value, force=force)

    def start(self, *args, **kwargs):
        """ give the start signal. """
        launcher.launch(self.scheduler)

    def stop(self):
        """ stop the handler. """
        self._stopped = True
        self._state.status = "stopped"
        self._queue.put_nowait(None)
