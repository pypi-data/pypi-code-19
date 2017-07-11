# botlib/engine.py
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

""" select.epoll event loop, easily interrup_table esp. versus a blocking event loop. """

from .error import EDISCONNECT, ERESUME
from .launcher import Launcher
from .handler import Handler
from .object import Object
from .register import Register

import logging
import select
import queue
import time

READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT

class Engine(Launcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected.clear()
        self._handlers = Register()
        self._queue = queue.Queue()
        self._poll = select.epoll()
        self._resume = Object()
        self._state.status = "running"
        self._time.start = time.time()

    def dispatch(self, event):
        event.parse()
        for handler in self._handlers.get(event._parsed.cmnd, []):
            try:
                handler(event)
            except Exception as ex:
                logging.error(get_exception())

    def select(self):
        stopped = False
        while self._state.status:
            if stopped:
                break
            for event in self.events():
                if not event:
                    stopped = True
                    break
                self._counter.events = self._counter.events + 1
                self.launch(self.dispatch, event, name=event._parsed.cmnd)
                self._time.latest = time.time()

    def events(self):
        try:
            fdlist = self._poll.poll()
        except ValueError:
            yield None
        for fd, event in fdlist:
            try:
                yield self.event()
            except ValueError:
                break
            except (ConnectionResetError,
                    BrokenPipeError,
                    EDISCONNECT) as ex:
                        self.connect()

    def register_fd(self, f):
        try:
            fd = f.fileno()
        except:
            fd = f
        if not fd:
            return fd
        logging.info("! engine on %s" % str(fd))
        #self._poll.register(fd, READ_ONLY)
        self._poll.register(fd)
        self._resume.fd = fd
        return fd

    def resume(self):
        logging.info("! resume on %s" % self._resume.fd)
        self._poll = select.epoll.fromfd(self._resume.fd)

    def start(self, *args, **kwargs):
        super().start()
        self.launch(self.select)

    def stop(self):
        self._status = ""
        try:
            self._poll.unregister(self._resume.fd)
        except:
            pass
        try:
            self._poll.close()
        except:
            pass
