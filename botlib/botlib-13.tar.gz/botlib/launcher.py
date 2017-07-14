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

""" a launch launches threads (or tasks in this case). """

from .utils import name
from .object import Object
from .task import Task

import threading
import logging

class Launcher(Object):

    cc = "!"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks = []

    def waiter(self, thrs, timeout=3.0):
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
        self._counter.launched += 1
        t = Task()
        t.start()
        t.put(*args, **kwargs)
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
