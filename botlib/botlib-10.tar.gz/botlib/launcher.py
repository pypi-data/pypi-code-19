# mad/launch.py
#
#

""" a launch launches threads (or Tasks in this case). """

from botlib.utils import name

from .object import Object
from .task import Task

import threading
import logging

class Launcher(Object):

    cc = "!"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status = "init"
        self._tasks = []
        
    def waiter(self, thrs, timeout=None):
        result = []
        for thr in thrs:
            if not thr:
                continue
            logging.debug("# waiting for %s" % str(thr))
            try:
                res = thr.join(timeout)
            except KeyboardInterrupt:
                break
            result.append(res)
        return result

    def launch(self, *args, **kwargs):
        self._counter.launched += 1
        t = Task()
        t.put(*args)
        return t

    def kill(self, thrname=""):
        thrs = []
        for thr in self.running(thrname):
            self._counter.killed += len(thrs)
            logging.info("! killed %s" % str(thr))
            if "cancel" in dir(thr):
                thr.cancel() 
            elif "exit" in dir(thr):
                thr.exit()
            elif "stop" in dir(thr):
                thr.stop()
            else:
                continue
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
