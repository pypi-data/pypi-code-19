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

""" bot base class. """

from .engine import Engine
from .error import ENOTIMPLEMENTED
from .object import Object
from .utils import sname

import queue

class Bot(Engine):

    """ main bot class. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected = Object()
        self._type = str(type(self))
        self._outqueue = queue.Queue()
        self.channels = []
        self.cfg.fromdisk(self.type)

    def announce(self, txt):
        """ print text on joined channels. """
        if self.cfg.silent:
            return
        if not self.channels:
            self.raw(txt)
        for channel in self.channels:
            self.say(channel, txt)

    def connect(self):
        """ connect to server. """
        raise ENOTIMPLEMENTED()

    def disconnect(self):
        """ disconnect from the server. """
        pass

    def id(self, *args, **kwargs):
        return sname(self).lower() + "." + (self.cfg.server or "localhost")


    def join(self, channel, password=""):
        """ join a channel. """
        pass

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.join(channel)

    def out(self, channel, line):
        """ output text on channel. """
        self.say(channel, line)

    def raw(self, txt):
        """ send txt to server. """
        self._counter.raw += 1

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        pass

    def say(self, channel, txt):
        """ say something on a channel. """
        if type(txt) in [list, tuple]:
            txt = ",".join(txt)
        self.raw(txt)

    def start(self, *args, **kwargs):
        from .space import fleet, runtime
        fleet.add(self)
        super().start(*args, **kwargs)
        self._connected.ready()
