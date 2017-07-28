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

""" threaded loop to run tasks on. """

from .task import Task

import time

class Runner(Task):

    """ while loop handling events placed in a thread (should mimic a logical CPU). """

    def run(self):
        self.name = self.kwargs.get("name", "") or "Runner"
        self.setName(self.name)
        self._state.status = "running"
        self._connected.wait()
        while self._state.status:
            _func, args = self._queue.get()
            self._counter.events += 1
            if not self._state.status or not _func:
                break
            try:
                self._state.event = args[0]
            except IndexError:
                pass
            self.setName(self.kwargs.get("name", self.name))
            self._begin = time.time()
            try:
                self._result = _func(*args)
            except OSError as ex:
                self._state.status = str(ex)
            self._last = time.time()
            try:
                args[0].ready()
            except:
                pass
        self.ready()
        return self._result
