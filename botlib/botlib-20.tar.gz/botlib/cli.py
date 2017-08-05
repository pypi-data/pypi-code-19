# BOTLIB Framework to program bots
#
# botlib/cli.py
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

"""
    command line interfacce bot, gives a shell prompt to issue bot commands. 

"""

from .bot import Bot
from .event import Event

import sys

def init(*args, **kwargs):
    """ initialise a CLI bot, present prompt when done. """
    bot = CLI()
    bot.start()
    bot.prompt()
    return bot

class CLI(Bot):

    """ Command Line Interface Bot. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompted = False
        self.register_fd(sys.stdin)

    def dispatch(self, *args, **kwargs):
        from .space import kernel
        kernel.put(args[0])

    def event(self):
        e = Event()
        e.cc = self.cc
        e.origin = "root@shell"
        e.server = "localhost"
        e.btype = self.type
        e.txt = input()
        self.prompted = False
        e.txt = e.txt.rstrip()
        return e

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        if self.prompted:
            return
        self.prompted = True
        if args and args[0]:
            txt = args[0]
        else:
            txt = "> "
        sys.stdout.write(txt)
        sys.stdout.flush()

    def raw(self, txt):
        """ output txt to sys.stdout """
        sys.stdout.write(str(txt))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def start(self, *args, **kwargs):
        super().start()
        self._connected.ready()
