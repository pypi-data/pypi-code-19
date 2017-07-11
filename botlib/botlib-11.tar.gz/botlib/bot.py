# botlib/bot.py
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

""" bot base class. """

from .error import ENOTIMPLEMENTED
from .launcher import Launcher
from .handler import Handler
from .engine import Engine
from .utils import sname

import queue

class Bot(Engine):

    """
        main bot class.

        >>> from botlib.bot import Bot
        >>> bot = Bot()
        >>> bot.connect()

    """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        self._connected.ready()

    def disconnect(self):
        """ disconnect from the server. """
        pass

    def event(self, *args, **kwargs):
        """ virtual method returning a event from the bot. """
        raise ENOTIMPLEMENTED

    def exit(self):
        self.put(None)

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
        super().start(*args, **kwargs)
        self._connected.ready()
        fleet.add(self)
