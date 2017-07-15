# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" select.epoll event loop, easily interrup_table esp. versus a blocking event loop. """

from .error import EDISCONNECT, ERESUME, ENOTIMPLEMENTED
from .handler import Handler
from .object import Object
from .register import Register
from .trace import get_exception
from .utils import name

import logging
import select
import queue
import time

READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT
EDGE = select.EPOLLIN  | select.EPOLLOUT | select.EPOLLET

class Engine(Handler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fds = []
        self._poll = select.epoll()
        self._resume = Object()
        self._state.status = "running"
        self._stopped = False
        self._time.start = time.time()

    def select(self):
        from .space import fleet, kernel, launcher
        while not self._stopped:
            for event in self.events():
                self._counter.events = self._counter.events + 1
                self.put(event)
                self._time.latest = time.time()
        logging.info("! stop %s" % self._fds)
        fleet.remove(self)
        self._state.status = "stopped"

    def event(self):
        raise ENOTIMPLEMENTED()

    def events(self):
        fdlist = self._poll.poll()
        for fd, event in fdlist:
            yield self.event()

    def register_fd(self, fd):
        self._poll.register(fd)
        self._fds.append(fd.fileno())
        logging.info("! engine on %s" % self._fds)
        return fd

    def resume(self):
        logging.info("! resume on %s" % self._resume.fd)
        self._poll = select.epoll.fromfd(self._resume.fd)

    def start(self, *args, **kwargs):
        from .space import launcher
        launcher.launch(self.select)
        super().start()

    def stop(self):
        logging.info("! stop %s" % self._fds)
        self._stopped = True
        for fd in self._fds:
            self._poll.unregister(fd)
        #self._poll.close()
