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


""" bot base class. """

from .engine import Engine
from .error import ENOTIMPLEMENTED
from .handler import Handler
from .launcher import Launcher
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

    def connect(self, *args, **kwargs):
        """ connect to server. """
        raise ENOTIMPLEMENTED()

    def disconnect(self):
        """ disconnect from the server. """
        pass

    def id(self, *args, **kwargs):
        return sname(self).lower() + "." + (self.cfg.server or "localhost")

    def join(self, channel):
        """ join a channel. """
        pass

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.join(channel)

    def out(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        """ send txt to server. """
        self._counter.raw += 1

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        pass

    def say(self, channel, txt):
        """ say something on a channel. """
        self.raw(str(txt).strip())

    def start(self, *args, **kwargs):
        from .space import fleet, runtime
        fleet.add(self)
        super().start(*args, **kwargs)
        self._connected.ready()
