# BOTLIB Framework to program bots
#
# botlib/runner.py
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
