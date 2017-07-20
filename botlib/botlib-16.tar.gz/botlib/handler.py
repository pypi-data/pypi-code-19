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

""" schedule events. """

from .object import Default, Object
from .register import Register

import queue
import time

class Handler(Object):

    """
        A Handler handles events pushed to it. Handlers can be threaded,
        e.g. start a thread on every event received, or not threaded in which
        case the event is handeled in loop.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers = Register()
        self._queue = queue.Queue()
        self._running = False
        self._stopped = False
        self._time.start = time.time()
        self._threaded = kwargs.get("threaded", True)
        self._counter = Default(default=0)
        self._state = Object()

    def dispatch(self, event):
        """ method to overload to determine how a event should be handled. """
        event.handle()

    def handler(self, event):
        """ basic handler function, define handling of the event. """
        from .space import launcher
        if self._threaded:
            thr = launcher.launch(self.dispatch, event)
            if thr and thr not in event._thrs:
               event._thrs.append(thr)
        else:
            self.dispatch(event)

    def scheduler(self, timeout=None):
        """ main loop of the Handler. """
        self._state.status = "running"
        self._time.latest = time.time()
        while not self._stopped:
            self._counter.nr += 1
            event = self._queue.get(timeout=timeout)
            self.handler(event)
        self._state.status = "stopped"

    def prompt(self, *args, **kwargs):
        """ virtual handler to display a prompt. """
        pass

    def put(self, *args, **kwargs):
        """ put an event to the handler. """
        time.sleep(0.001)
        self._queue.put_nowait(*args, **kwargs)

    def register(self, key, val, force=False):
        """ register a handler. """
        self._handlers.register(key, val, force=force)

    def start(self, *args, **kwargs):
        """ give the start signal. """
        from .space import launcher
        launcher.launch(self.scheduler)

    def stop(self):
        """ stop the handler. """
        self._stopped = True
        self._state.status = "stopped"
        self._queue.put_nowait(None)
