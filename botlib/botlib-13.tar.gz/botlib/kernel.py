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

""" program boot and module loading. """

from .event import Event
from .handler import Handler
from .log import loglevel
from .mods import Mods
from .object import Config, Default, Object
from .raw import RAW
from .utils import name, set_completer

import botlib
import logging
import os
import sys
import time

class Kernel(Handler, Mods):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._booted = Object()
        self._finished = Object()
        self._time = Default(default=0)
     
    def announce(self, txt):
        """ announce txt on all fleet bot. """
        from .space import fleet
        for bot in fleet:
            bot.announce(txt)

    def boot(self, cfgin):
        """ start the kernel. """
        from .space import alias, cfg, fleet, launcher, load
        dosave = False
        thrs = []
        self._time.start = time.time()
        cfg.update(cfgin)
        if not cfg.workdir:
            cfg.workdir = os.path.join(cfg.homedir, ".botdata")
        else:
            cfg.changed = True
        if cfg.user:
           cfg.shell = True
           cfg.loglevel = cfg.loglevel or "warn"
           cfg.banner = True
           cfg.license = True
        if cfg.banner:
            print("%s #%s\n" % (cfg.name.upper(), cfg.version))
        if cfg.license:
            print(botlib.__license__)
        if cfg.loglevel in ["debug", "info", "warn"]:
           cfg.verbose = True
        loglevel(cfg.loglevel or "error")
        self.load_eggs()
        self.initialize()
        self.start()
        if cfg.args:
            e = self.once(" ".join(cfg.args))
            e.wait()
            self.ready()
            return self
        for name in cfg.mods.split(","):
            if name:
                self.walk(name)
        for modname in cfg.needed:
            self.init(modname)
        if cfg.all or cfg.init:
            for pname in cfg.packages:
                for modname in self.modules(pname):
                    n = modname.split(".")[-1]
                    if modname in cfg.ignore and n not in cfg.init:
                        continue
                    if cfg.all or n in cfg.init.split(","):
                        thr = self.init(modname)
                        if thr:
                            thrs.append(thr)
        launcher.waiter(thrs)
        if cfg.shell and not cfg.all:
            thr = self.init("botlib.cli")
            thr.join()
        for bot in fleet:
            bot._connected.wait(3.0)
        if cfg.all or cfg.shell or cfg.init:
            for bot in fleet:
                 bot.wait()
        self.ready()
        return self

    def cmnd(self, txt):
        """ execute a command based on txt. """
        from .space import fleet
        bot = RAW()
        fleet.add(bot)
        event = Event()
        event.cc = ""
        event.origin = "root@shell"
        event.channel = "#botlib"
        event.server = "localhost"
        event.btype = bot.type
        event.txt = txt
        event.parse()
        return event

    def handler(self, event):
        """ handle an event. """
        from .space import kernel
        event.parse()
        self._state.running = event._parsed.cmnd
        handlers = self.get_handlers(event._parsed.cmnd)
        for handler in handlers:
            logging.info("! dispatch %s" % name(handler))
            handler(event)
        event.show()
        event.prompt()
        return self

    def load_config(self):
        from .space import cfg
        c = Config().load(os.path.join(cfg.bootdir, "runtime", "cfg"))
        cfg.update(c)

    def load_eggs(self):
        from .space import cfg
        for fn in os.listdir(os.getcwd()):
            if fn.endswith(".egg"):
                if cfg.verbose:
                    logging.info("! load %s" % fn)
                sys.path.insert(0, fn)

    def once(self, txt):
        """ run once command. """
        e = self.cmnd(txt)
        self.handler(e)
        return e

    def shutdown(self, close=False, write=False):
        """ stop bot, services and plugins. """
        from .space import cfg, fleet, kernel, partyline, runtime
        logging.info("! shutdown")
        logging.info("")
        event = Event()
        event.txt = "shutdown"
        event.server = "kernel"
        thrs = []
        if close:
            for bot in fleet:
                if "stop" in dir(bot):
                    bot.stop()
                elif "exit" in dir(bot):
                    bot.exit()
                bot.ready()
            for key, mod in self._table.items():
                try:
                    mod.shutdown(event)
                except AttributeError:
                    continue
        if write or cfg.write:
            partyline.sync(os.path.join(cfg.bootdir, "runtime", "partyline"))
            fleet.sync(os.path.join(cfg.bootdir, "runtime", "fleet"))
            kernel.sync(os.path.join(cfg.bootdir, "runtime", "kernel"))
            cfg.sync(os.path.join(cfg.bootdir, "runtime", "cfg"))
        if cfg.test:
            for ex in exceptions:
                print(ex)
        self.ready()
