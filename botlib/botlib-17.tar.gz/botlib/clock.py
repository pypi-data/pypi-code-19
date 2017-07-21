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

""" timer, repeater and other clock based classes. """

from .event import Event
from .object import Default, Config, Object
from .trace import get_exception
from .utils import name

import os
import logging
import threading
import time

start = 0

def init(*args, **kwargs):
    """ initialise timers stored on disk. """
    from .space import cfg, db, kernel, launcher
    cfg = Config(default=0).load(os.path.join(cfg.workdir, "runtime", "timer"))
    cfg.template("timer")
    timers = []
    for e in db.sequence("timer", cfg.latest):
        if e.done: continue
        if "time" not in e: continue
        if time.time() < int(e.time):
            timer = Timer(int(e.time), e.direct, e.txt)
            t = launcher.launch(timer.start)
            timers.append(t)
        else:
            cfg.last = int(e.time)
            cfg.save()
            e.done = True
            e.sync()
    return timers

class Timer(Object):

    """ call a function as x seconds of sleep. """

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep = sleep
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._name = kwargs.get("name", name(self.func))
        try:
            self._event = self.args[0]
        except:
            self._event = Event()

    def start(self):
        """ start the timer. """
        logging.info("! timer %s" % self._name)
        timer = threading.Timer(self.sleep, self.run, self.args, self.kwargs)
        timer.setDaemon(True)
        timer.setName(self._name)
        timer.sleep = self.sleep
        timer._event = self._event
        timer._state = Default(default="")
        timer._counter = Default(default=0)
        timer._time = Default(default=0)
        timer._time.start = time.time()
        timer._time.latest = time.time()
        timer._state.status = "waiting"
        timer.start()
        return timer

    def run(self, *args):
        """ run the registered function. """
        self._time.latest = time.time()
        self._counter.run += 1
        self.func(*self.args, **self.kwargs)

    def exit(self):
        """ cancel the timer. """
        self.cancel()

class Repeater(Timer):

    """ repeat an funcion every x seconds. """

    def run(self, *args, **kwargs):
        self.func(*self.args, **self.kwargs)
        self.start()
