# BOTLIB Framework to program bots
#
# botlib/worker.py
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

""" worker thread that handles submitted jobs through Worker.put(func, args, kwargs). """

from .object import Default, Object
from .clock import Repeater
from .launcher import Launcher
from .task import Task
from .trace import get_exception
from .utils import name as _name

import logging
import queue
import random
import threading
import time

class Worker(threading.Thread):

    """ Task are adapted Threads. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._busy = False
        self._counter = Default(default=0)
        self._error = Default()
        self._last = time.time()
        self._queue = queue.Queue()
        self._stopped = False
        self._results = []
        self._running = False
        self._state = Default()
        self._time = Default(default=0.0)
        self._time.start = time.time()

    def __iter__(self):
        """ return self as an iterator. """
        return self

    def __next__(self):
        """ yield next value. """
        for k in dir(self):
            yield k
        
    def since(self):
        """ show how many seconds till last function executed. """
        return time.time() - self._last

    def put(self, func, *args, **kwargs):
        """ put a func(args, kwargs) to work. """
        self._queue.put_nowait((func, args, kwargs))

    def run(self):
        """ run a loop that handles jobs. """
        self._running = True
        while not self._stopped:
            func, args, kwargs = self._queue.get()
            if self._stopped:
                break
            time.sleep(0.001)
            self._busy = True
            self._last = time.time()
            n = kwargs.get("name", _name(func))
            self.setName(n)
            if args:
                event = args[0]
                event.parse()
                n = event._parsed.cmnd
            self._state.cmnd = n
            self._counter.run += 1
            try:
                result = func(*args)
            except Exception as ex:
                result = None
                logging.error(get_exception())
            if kwargs.get("collect", None):
                self._results.append(result)
            self._busy = False
            if args:
                args[0].ready()
            if kwargs.get("once", None):
                break
        return self._results

    def stop(self):
        """ stop this worker. """
        self._stopped = True
        self.put((None, None, None))
        
class Pool(Launcher):

    """ Pool of workers, default to 10 instances. """

    def __init__(self, nr=10):
        super().__init__()
        self._workers = [] 
        self._nr = nr
        for x in range(nr):
            self.get_worker(str(x), True)
        repeater = Repeater(60, self.cleanup)
        repeater.start()

    def cleanup(self):
        """" cleanup idle workers. """
        for worker in self._workers[:self._nr]:
             if worker.since() > 30.0:
                 worker.stop()
                 self._workers.remove(worker)

    def get_worker(self, name="", force=False):
        """ return a worker from pool. """
        if not force:
            for worker in self._workers[:self._nr]:
                if worker._queue.empty() and not worker._busy:
                    return worker
        if force or len(self._workers) <= self._nr:
            worker = Worker(name=name)
            worker.start()        
            self._workers.append(worker)
            return worker
        else:
            return random.choice(self._workers)

    def put(self, *args, **kwargs):
        """ dispatch to the next idle worker thread. """
        func = args[0]
        worker = self.get_worker()
        worker.put(*args, **kwargs)
        return worker
