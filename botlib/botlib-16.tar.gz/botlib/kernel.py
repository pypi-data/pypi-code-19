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

""" program boot and module loading. """

from .event import Event
from .handler import Handler
from .launcher import Launcher
from .log import loglevel
from .object import Config, Default, Object
from .raw import RAW
from .register import Register
from .utils import cdir, set_completer

import importlib
import logging
import os
import pkgutil
import sys
import time
import types

class Kernel(Handler, Launcher):

    """
        Kernel object does the startup/shutdown of the bot.
        Call Kernel.boot() at the start of your program.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._booted = Object()
        self._cmnds = []
        self._finished = Object()
        self._handlers = Register()
        self._names = Register()
        self._scanned = False
        self._stopped = False
        self._table = Object()
        self._time = Default(default=0)
        self._threaded = True
        
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
            cfg.workdir = os.path.join(cfg.homedir, ".bot")
        else:
            cfg.changed = True
        if cfg.user:
            cfg.shell = True
            cfg.loglevel = cfg.loglevel or "warn"
            cfg.banner = True
            cfg.test = True
        if cfg.banner:
            print("%s #%s Framework to program bots\n" % (cfg.name.upper(), cfg.version))
        if cfg.loglevel in ["debug", "info", "warn"]:
            cfg.verbose = True
        if not os.path.exists(cfg.workdir):
            cdir(cfg.workdir)
        loglevel(cfg.loglevel or "error")
        logging.info("! loglevel %s" % cfg.loglevel)
        if cfg.eggs:
            self.load_eggs()
        if not self._names:
            p = os.path.join(cfg.workdir, "runtime", "kernel")
            try:
                k = Object().load(p)
                if "_names" in k:
                    self._names.update(k._names)
            except ValueError:
                pass
        if not self._names or cfg.write:
            self._names = Register()
            self.walk("botlib", True)
            cfg.write = True
        if cfg.write:
            self.sync(os.path.join(cfg.workdir, "runtime", "kernel"))
        if not self._cmnds:
            self._cmnds = sorted(set([cmnd for cmnd in self._names.keys()]))
        set_completer(self._cmnds)
        load()
        self.start()
        if cfg.args:
            e = self.once(" ".join(cfg.args))
            e.wait()
            self.ready()
            return self
        for modname in cfg.mods.split(","):
            if modname:
                self.load(modname)
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
        for bot in fleet:
            bot._connected.wait(3.0)
        if cfg.shell and not cfg.all:
            thr = self.init("botlib.cli")
            if thr:
                thr.join()
        if cfg.all or cfg.shell or cfg.init:
            for bot in fleet:
                bot.wait()
        self.ready()
        return self

    def cmnd(self, txt):
        """ execute a command based on txt. """
        from .space import fleet
        bot = RAW()
        bot.verbose = True
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

    def direct(self, name, package=None):
        """ import a module directly, not storing it in the cache. """
        logging.info("! direct %s" % name)
        return importlib.import_module(name, package)

    def get_handlers(self, cmnd):
        """ search for a function registered by command. """
        from .space import alias, cfg, launcher
        oldcmnd = cmnd
        cmnd = alias.get(cmnd, cmnd)
        funcs = self._handlers.get(cmnd, [])
        if not funcs:
            funcs = self._handlers.get(oldcmnd, [])
            if not funcs:
                modnames = self._names.get(cmnd, [])
                for modname in modnames:
                    self.load(modname, True)
                    funcs = self._handlers.get(cmnd, [])
                    break
        return funcs

    def init(self, modname):
        """ initialize a module. """
        from .space import launcher
        event = Event()
        n = modname.split(".")[-1]
        mod = self._table.get(modname, None)
        if not mod or type(mod) == str:
            mod = self.load(modname)
        if mod and "init" in dir(mod):
            thr = launcher.launch(mod.init, event, name="%s.init" % n)
            thr.join()

    def list(self, name):
        """ list all functions found in a module. """
        for modname in self.modules(name):
            mod = self.direct(modname)
            for key in dir(mod):
                if key in ["init", "shutdown"]:
                    continue
                obj = getattr(mod, key, None)
                if obj and type(obj) == types.FunctionType:
                    if "event" in obj.__code__.co_varnames:
                        yield key

    def load(self, modname, force=False):
        """ load a module. """
        if not force and modname in self._table:
            return self._table[modname]
        self._table[modname] = self.direct(modname)
        self.register(modname)
        return self._table[modname]
        
    def register(self, modname, force=False):
        mod = self.load(modname, force=force)
        for key in dir(mod):
            if key.startswith("_"):
                continue
            obj = getattr(mod, key, None)
            if obj and type(obj) == types.FunctionType:
                if "event" in obj.__code__.co_varnames:
                    self._names.register(key, modname)
                    if key not in ["init", "shutdown"]:
                        self._handlers.register(key, obj)
        if force:
            self._table[modname] = mod
        return self._table[modname]

    def load_config(self):
        """ load cfg from file. """
        from .space import cfg
        c = Config().load(os.path.join(cfg.workdir, "runtime", "cfg"))
        cfg.update(c)

    def load_eggs(self):
        """ load eggs from current directory. """
        from .space import cfg
        for fn in os.listdir(os.getcwd()):
            if fn.endswith(".egg"):
                if cfg.verbose:
                    logging.info("! egg %s" % fn)
                sys.path.insert(0, fn)

    def modules(self, name):
        """ return a list of modules in the named packages or cfg.packages if no module name is provided. """
        package = self.direct(name)
        for pkg in pkgutil.walk_packages(package.__path__, name + "."):
            yield pkg[1]

    def once(self, txt):
        """ run once command. """
        e = self.cmnd(txt)
        e.handle()
        return e

    def reload(self, name, force=False, event=None):
        """ reload module. """
        e = event or Event()
        if name not in self._table:
            return
        self._table[name].shutdown(e)
        self.load(name, force)
        if force:
            self._table[name].init(e)
        if name in self._table:
            return self._table[name]

    def shutdown(self, close=False, write=False):
        """ stop bot, services and plugins. """
        from .space import cfg, exceptions, fleet, kernel, partyline, runtime
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
            partyline.sync(os.path.join(cfg.workdir, "runtime", "partyline"))
            fleet.sync(os.path.join(cfg.workdir, "runtime", "fleet"))
            kernel.sync(os.path.join(cfg.workdir, "runtime", "kernel"))
            cfg.sync(os.path.join(cfg.workdir, "runtime", "cfg"))
        if cfg.test:
            for ex in exceptions:
                print(ex)
        self.ready()

    def walk(self, name, init=False, force=False):
        """ return all modules in a package. """
        self._scanned = True  
        for modname in sorted(list(self.modules(name))):
            self.register(modname, force)
