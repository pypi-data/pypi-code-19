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
        self.register(sys.stdin)

    def dispatcher(self, event):
        kernel.put(event)
        
    def event(self, *args, **kwargs):
        e = Event()
        e.cc = self.cc
        e.origin = "root@shell"
        e.server = "localhost"
        e.btype = self.type
        e.txt = input()
        e.txt = e.txt.rstrip()
        return e

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
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
