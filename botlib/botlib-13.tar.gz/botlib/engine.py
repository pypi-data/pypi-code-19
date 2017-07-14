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

class Engine(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fds = []
        self._handlers = Register()
        self._queue = queue.Queue()
        self._poll = select.epoll()
        self._resume = Object()
        self._state.status = "running"
        self._stopped = False
        self._time.start = time.time()
        self._threaded = kwargs.get("threaded", False)

    def dispatcher(self, event):
        for handler in self._handlers.get(event._parsed.cmnd, []):
            handler(event)

    def select(self):
        from .space import fleet
        while not self._stopped:
            for event in self.events():
                self._counter.events = self._counter.events + 1
                try:
                    self.dispatcher(event)
                except:
                    logging.error(get_exception())
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

    def register(self, fd):
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

    def stop(self):
        logging.info("! stop %s" % self._fds)
        self._stopped = True
        for fd in self._fds:
            self._poll.unregister(fd)
        self._poll.close()
