# BOTLIB Framework to program bots
#
# botlib/handler.py
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

""" schedule events. """

from .error import ENOCOMMAND
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

    def scheduler(self):
        """ main loop of the Handler. """
        from .space import pool
        self._state.status = "run"
        self._time.latest = time.time()
        while not self._stopped:
            self._counter.nr += 1
            event = self._queue.get()
            if not event:
                break
            pool.put(self.dispatch, event)
        self._state.status = "stop"

    def prompt(self, *args, **kwargs):
        """ virtual handler to display a prompt. """
        pass

    def put(self, *args, **kwargs):
        """ put an event to the handler. """
        self._queue.put_nowait(*args, **kwargs)

    def register(self, key, val, force=False):
        """ register a handler. """
        self._handlers.register(key, val, force=force)

    def start(self, *args, **kwargs):
        """ give the start signal. """
        from .space import launcher
        self._stopped = False
        launcher.launch(self.scheduler)

    def stop(self):
        """ stop the handler. """
        self._stopped = True
        self._state.status = "stop"
        self._queue.put(None)
