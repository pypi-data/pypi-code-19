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

""" a launcher launches threads (or tasks in this case). """

from .event import Event
from .object import Object
from .task import Task
from .utils import name

import threading
import logging

class Launcher(Object):

    """ Laucher is able to launch a Task (see task.py). """

    cc = "!"

    def waiter(self, thrs, timeout=0):
        """ wait for tasks to finish. """
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
        """ launc a function with argument in it's own thread. """
        self._counter.launch += 1
        func = args[0]
        n = kwargs.get("name", name(func))
        if len(args) > 1:
            event = args[1]
            try:
                event.parse()
                n = event._parsed.cmnd
            except:
                pass
            t = Task(None, func, n, (event,), {}, daemon=True)
        else:
            e = Event()
            t = Task(None, func, n, (), {}, daemon=True)
        t.start()
        return t

    def kill(self, thrname=""):
        """ kill tasks matching the provided name. """
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

    def running(self, tname=""):
        """ show what tasks are running. """
        for thr in threading.enumerate():
            if str(thr).startswith("<_"):
                continue
            yield thr
