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

    def dispatch(self, event):
        from .space import kernel
        kernel.put(event)

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
