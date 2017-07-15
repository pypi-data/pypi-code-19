# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" schedule events. """

from .object import Object
from .register import Register
from .trace import get_exception

import logging
import queue
import time

class Handler(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._slow = []
        self._handlers = Register()
        self._queue = queue.Queue()
        self._running = False
        self._stopped = False
        self._time.start = time.time()
        self._threaded = kwargs.get("threaded", True)

    def dispatch(self, event):
        event.handle()

    def handler(self, event):
        from .space import launcher
        _funcs = event.prep()
        threaded = False
        for func in _funcs:
            if func in self._slow:
                threaded = True
                break
        if threaded:
            launcher.launch(self.dispatch, event, name=event._parsed.cmnd)
        else:
            starttime = time.time()
            self.dispatch(event)
            endtime = time.time()
            if endtime - starttime > 1.0:
                for func in event._funcs:
                    if func not in self._slow:
                        self._slow.append(func)

    def scheduler(self, timeout=None):
        self._state.status = "running"
        self._time.latest = time.time()
        while not self._stopped:
            event = self._queue.get(timeout=timeout)
            self._counter.events = self._counter.events + 1
            self.handler(event)

    def prompt(self, *args, **kwargs):
        """ virtual handler to display a prompt. """
        pass

    def put(self, *args, **kwargs):
        """ put an event to the handler. """
        self._queue.put_nowait(*args, **kwargs)

    def register(self, key, value, force=False):
        """ register a handler. """
        self._handlers.register(key, value, force=force)

    def start(self, *args, **kwargs):
        """ give the start signal. """
        from .space import launcher
        launcher.launch(self.scheduler)

    def stop(self):
        """ stop the handler. """
        self._stopped = True
        self._state.status = "stopped"
        self._queue.put_nowait(None)
