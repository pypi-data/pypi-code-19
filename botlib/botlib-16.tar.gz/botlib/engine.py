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

""" select.epoll event loop, easily interrup_table esp. versus a blocking event loop. """

from .error import ENOTIMPLEMENTED, EDISCONNECT
from .handler import Handler
from .object import Object
from .trace import get_exception

import logging
import select
import time

READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT
EDGE = select.EPOLLIN  | select.EPOLLOUT | select.EPOLLET

class Engine(Handler):

    """
        An engine is a front-end class to check for input and if ready ask the inherited class to construct an event based on this input.
        The created event is pushed to the base class (Handler) thats takes care of further event handling.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fds = []
        self._poll = select.epoll()
        self._resume = Object()
        self._state.status = "running"
        self._stopped = False
        self._time.start = time.time()

    def select(self):
        """ select loop defering the creation of events to the bot's class. """
        from .space import fleet, kernel, launcher
        while not self._stopped:
            for event in self.events():
                if event:
                    self.put(event)
                self._time.latest = time.time()
        logging.info("! stop %s" % self._fds)
        fleet.remove(self)
        self._state.status = "stopped"

    def event(self):
        """ virutal method to create an event, should be inherited. """
        raise ENOTIMPLEMENTED()

    def events(self):
        """ use poll to see if a bot is ready to receive input and if so, call the event() method to create an event from this input. """
        fdlist = self._poll.poll()
        for fd, event in fdlist:
            try:
                yield self.event()
            except (ConnectionResetError,
                    BrokenPipeError,
                    EDISCONNECT) as ex:
                        self.connect()
                        self.unregister_fd(fd)

    def register_fd(self, fd):
        """ register filedescriptors to check for input. """
        self._poll.register(fd)
        self._fds.append(fd.fileno())
        self._counter.fd = ",".join([str(x) for x in self._fds])
        logging.info("! engine on %s" % ",".join(str(x) for x in self._fds))
        return fd

    def resume(self):
        """ code to run when a engine has to be resumed. """
        logging.info("! resume on %s" % self._resume.fd)
        self._poll = select.epoll.fromfd(self._resume.fd)

    def start(self, *args, **kwargs):
        """ start the select() method in it's own thread. """
        from .space import launcher
        launcher.launch(self.select)
        super().start()

    def stop(self):
        """ unregister all filedescriptors and close the polling object. """
        logging.info("! stop %s" % self._fds)
        super().stop()
        for fd in self._fds:
            try:
                self.unregister_fd(fd)
            except FileNotFoundError:
                pass

    def unregister_fd(self, fd):
        if fd in self._fds:
            self._fds.remove(fd)
        try:
            self._poll.unregister(fd)
        except FileNotFoundError:
            pass
