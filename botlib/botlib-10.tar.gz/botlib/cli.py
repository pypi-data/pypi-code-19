# botlib/cli.py
#
#

""" bot classes. """

from .bot import Bot
from .event import Event
from .space import fleet, runtime

import logging
import select
import sys

def init(event):
    bot = CLI()
    bot.start()
    return bot

def shutdown(event):
    bot = fleet.get_bot("cli")
    bot.stop()
    launcher.kill("cli")

class CLI(Bot):

    """
        Command Line Interface Bot.

        >>> from bot.cli import CLI
        >>> bot = CLI()
        >>> print(bot)

    """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_fd(sys.stdin)

    def dispatch(self, event):
        thr = event.handle()
        thr.join()
        self.prompt()
        
    def event(self):
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
        if args:
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

    def register_fd(self, f):
        """ register an file or filedescriptor. """
        try:
            fd = f.fileno()
        except:
            fd = f
        self._poll.register(fd,
                            select.EPOLLIN  | 
                            select.EPOLLOUT | 
                            select.EPOLLET)
        logging.info("# engine on %s" % str(fd))
        self._resume.fd = fd
        return fd

    def start(self):
        super().prompt()
        self._connected.ready()
        super().start()
