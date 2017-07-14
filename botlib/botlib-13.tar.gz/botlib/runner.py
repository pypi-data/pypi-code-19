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

""" threaded loop to run tasks on. """

from .task import Task

import logging
import time

class Runner(Task):

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
