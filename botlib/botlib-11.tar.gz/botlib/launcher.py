# botlib/launcher.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

""" a launch launches threads (or tasks in this case). """

from botlib.utils import name

from .object import Object
from .task import Task

import threading
import logging

class Launcher(Object):

    cc = "!"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks = []

    def waiter(self, thrs, timeout=None):
        result = []
        for thr in thrs:
            if not thr:
                continue
            logging.debug("waiting for %s" % str(thr))
            try:
                res = thr.join(timeout)
            except KeyboardInterrupt:
                break
            result.append(res)
        return result

    def launch(self, *args, **kwargs):
        if args:
            logging.info("! %s" % args[0])
        self._counter.launched += 1
        t = Task()
        t.put(*args)
        return t

    def kill(self, thrname=""):
        thrs = []
        for thr in self.running(thrname):
            self._counter.killed += len(thrs)
            if "cancel" in dir(thr):
                thr.cancel() 
            elif "exit" in dir(thr):
                thr.exit()
            elif "stop" in dir(thr):
                thr.stop()
            else:
                continue
            logging.info("! killed %s" % str(thr))
            thrs.append(thr)
        return thrs

    def running(self, name=""):
        n = str(name).upper()
        for thr in threading.enumerate():
            thrname = str(thr).upper()
            if thrname.startswith("<_"):
                continue
            if n not in thrname:
                continue
            yield thr

    def start(self, *args, **kwargs):
        """ virtual start method. """
        pass
