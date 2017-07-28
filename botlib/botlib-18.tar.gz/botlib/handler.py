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
        self._names = Register()
        self._queue = queue.Queue()
        self._running = False
        self._stopped = False
        self._time.start = time.time()
        self._threaded = kwargs.get("threaded", True)
        self._counter = Default(default=0)
        self._state = Object()

    def handler(self, *args, **kwargs):
        """ basic handler function, define handling of the event. """
        from .space import launcher
        event = args[0]
        if self._threaded:
            thr = launcher.launch(self.dispatch, *args, **kwargs)
            if thr and thr not in event._thrs:
               event._thrs.append(thr)
        else:
            self.dispatch(event)

    def dispatch(self, *args, **kwargs):
        """ handle an event. """
        event = args[0]
        event.parse()
        event._funcs = self.get_handlers(event._parsed.cmnd)
        event.dispatch()
        event.show()
        event.prompt()
        event.ready()
        return event._result

    def get_handlers(self, cmnd):
        """ search for a function registered by command. """
        from .space import alias, cfg, launcher
        oldcmnd = cmnd
        cmnd = alias.get(cmnd, cmnd)
        funcs = self._handlers.get(cmnd, [])
        if not funcs:
            funcs = self._handlers.get(oldcmnd, [])
            if not funcs:
                modnames = self._names.get(cmnd, [])
                for modname in modnames:
                    self.load(modname, True)
                    funcs = self._handlers.get(cmnd, [])
                    break
        return funcs

    def scheduler(self, *args, **kwargs):
        """ main loop of the Handler. """
        self._state.status = "run"
        self._time.latest = time.time()
        while not self._stopped:
            self._counter.nr += 1
            event = self._queue.get()
            if not event:
                break
            self.handler(event)
        self._state.status = "stop"

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
        self._state.status = "stop"
        self._queue.put(None)
