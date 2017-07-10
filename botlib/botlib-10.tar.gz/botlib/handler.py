# mad/scheduler.py
#
#

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
            logging.warn("# handler %s" % str(handler))
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
            
    def prompt(self):
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
        logging.warn("# start %s" % self.id())
        self.launch(self.scheduler, daemon=True)
        super().start(*args, **kwargs)
        self._connected.ready()

    def stop(self):
        """ stop the handler. """
        self._state.status = ""
        self._queue.put_nowait(None)
