# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" bot classes. """

from .bot import Bot
from .event import Event
from .space import kernel, fleet, launcher, runtime

import logging
import select
import sys

def init(event):
    bot = CLI()
    bot.start()
    bot.prompt()
    return bot

def shutdown(event):
    bots = fleet.get_type("cli")
    for bot in bots:
        bot.stop()

class CLI(Bot):

    """ Command Line Interface Bot. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompted = False
        self.register_fd(sys.stdin)

    def event(self, *args, **kwargs):
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

    def start(self):
        super().start()
        self._connected.ready()
