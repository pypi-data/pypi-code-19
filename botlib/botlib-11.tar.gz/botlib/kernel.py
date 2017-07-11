# botlib/kernel.py
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

""" program boot and module loading. """

from .db import Db
from .compose import compose
from .error import ENOMODULE
from .event import Event
from .fleet import Fleet
from .launcher import Launcher
from .object import Default, Object, Config
from .handler import Handler
from .register import Register
from .template import template
from .log import loglevel
from .raw import RAW
from .utils import set_completer, pathname
from .trace import get_exception

import botlib
import logging
import importlib
import os
import pkgutil
import queue
import shutil
import sys
import time
import types

class Kernel(Handler, Launcher, Db):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._booted = Object()
        self._cbs = Register()
        self._cmnds = []
        self._finished = Object()
        self._names = Register()
        self._table = Object()
        self._time = Default(default=0)
     
    def announce(self, txt):
        """ announce txt on all fleet bot. """
        from .space import fleet
        for bot in fleet:
            bot.announce(txt)

    def boot(self, cfgin):
        """ start the kernel. """
        from .space import alias, cfg, fleet, load, users, ENOWORKDIR
        self._time.start = time.time()
        for fn in os.listdir(os.getcwd()):
            if fn.endswith(".egg"):
                if cfg.verbose:
                    logging.info("! load %s" % fn)
                sys.path.insert(0, fn)
        cfg.update(cfgin)
        if cfg.workdir:
            cfg.changed = True
        if cfg.user:
            cfg.banner = True
            cfg.shell = True
            cfg.verbose = True
            cfg.loglevel = cfg.loglevel or "warn"
            cfg.wait = True
        if cfg.test:
            cfg.workdir = os.path.abspath(os.path.join(os.getcwd(), "data"))
            cfg.changed = True
        if cfg.scan:
            if "workdirs" in c and c.workdirs:
                cfg.workdirs = c.workdirs
        if cfg.write:
            cfg.workdirs = []
            dosave = True
        logger = loglevel(cfg.loglevel or "error", cfg.logdir)
        logger.propagate = False
        thrs = []
        logging.info("! boot %s" % cfg.loglevel)
        if cfg.banner:
            print("%s #%s\n" % (cfg.name.upper(), cfg.version))
        cfg.logdir = cfg.logdir or os.path.join(cfg.homedir, ".botlog")
        if cfg.shell:
            cfg.init = "cli," + cfg.init
            cfg.wait = True
        if cfg.args:
            e = self.once(" ".join(cfg.args))
            if e:
                e.wait()
            self.ready()
            return self
        if not cfg.workdir:
            cfg.workdir = os.path.join(cfg.homedir, ".botdata")
        if not os.path.isdir(cfg.bootdir):
            os.mkdir(cfg.bootdir)
        if not os.path.isdir(cfg.workdir):
            os.mkdir(cfg.workdir)
        dosave = False
        load()
        if not self._names and not cfg.write:
            k = Kernel().load(os.path.join(cfg.bootdir, "runtime", "kernel"))
            self._names.update(k._names)
            c = Config().load(os.path.join(cfg.bootdir, "runtime", "cfg"))
        if cfg.yes or cfg.write or not self._names:
            self.walk("botlib")
            self.sync(os.path.join(cfg.bootdir, "runtime", "kernel"))
        for name in cfg.mods.split(","):
            if name:
                self.walk(name)
        self.start()
        for modname in cfg.needed:
            thr = self.init(modname)
            thrs.append(thr)
        if cfg.all or cfg.init:
            for pname in cfg.packages:
                for modname in self.modules(pname):
                    n = modname.split(".")[-1]
                    if modname in cfg.ignore and n not in cfg.init:
                        continue
                    if cfg.all or n in cfg.init.split(","):
                        self.init(modname)
        if not self._cmnds:
            self._cmnds = sorted(set([cmnd for cmnd in self._names.keys()]))
        set_completer(self._cmnds)
        if dosave:
            cfg.sync(os.path.join(cfg.bootdir, "runtime", "cfg"))
        self.start()
        if cfg.wait:
            for bot in fleet:
                bot._connected.wait(3.0)
        logging.info("! end of boot.")
        for bot in fleet:
            bot.prompt()
        if cfg.shell:
            for bot in fleet:
                bot.wait()
        self.ready()
        return self
               
    def callcb(self, event): 
        try:
            _cbs = self._cbs[event.origin]
        except KeyError:
            _cbs = []
        for cb in _cbs:
            cb(event)

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

    def direct(self, name, package=None):
        """ import a module directly, not storing it in the cache. """
        return importlib.import_module(name, package)

    def dispatch(self, event):
        """ dispatch an event. """
        thr = event.handle()
        thr.join()
        self._time.last = time.time()

    def get_funcs(self, cmnd):
        """ search for a function registered by command. """
        from botlib.space import alias
        oldcmnd = cmnd
        cmnd = alias.get(cmnd, cmnd)
        funcs = self._handlers.get(cmnd, [])
        if not funcs:
            funcs = self._handlers.get(oldcmnd, [])
            if not funcs:
                modnames = self._names.get(cmnd, [])
                if not modnames and cmnd in self._cmnds:
                    self.walk("botlib")
                for modname in modnames:
                    try:
                        self.loading(modname)
                    except Exception as ex:
                        logging.error(get_exception())
                    funcs = self._handlers.get(cmnd, [])
        return funcs

    def init(self, modname):
        """ initialize a module. """
        from botlib.space import cfg
        event = Event()
        n = modname.split(".")[-1]
        mod = self._table.get(modname, None)
        if not mod or type(mod) == str:
            mod = self.load_mod(modname)
        if mod and "init" in dir(mod):
            if mod.init:
                thr = self.launch(mod.init, event)
                return thr

    def list(self, name):
        """ list all functions found in a module. """
        for modname in self.modules(name):
            mod = self.direct(modname)
            for key in dir(mod):
                if key in ["init", "shutdown"]:
                    continue
                object = getattr(mod, key, None)
                if object and type(object) == types.FunctionType:
                    if "event" in object.__code__.co_varnames:
                        yield key

    def load_mod(self, modname, force=True):
        """ load a module and if force is sset to True, put in in the cache, """
        if force or modname not in self._table:
            mod = self.direct(modname)
            self._table[modname] = mod
        return self._table[modname]

    def loading(self, modname, force=True):
        """ load a module. """
        logging.info("! loading %s" % modname)
        if force:
            mod = self.load_mod(modname)
        else:
            mod = self.direct(modname)
        if not mod:
            raise ENOMODULE(modname)
        res = Object()
        for key in dir(mod):
            if key.startswith("_"):
                continue
            object = getattr(mod, key, None)
            if object and type(object) == types.FunctionType:
                if "event" in object.__code__.co_varnames:
                   if key.startswith("cb_"): 
                       k = key.split("cb_")[-1]
                       self._cbs.register(key, object)
                   else:
                       self._names.register(key, modname)
                       if key not in ["init", "shutdown"]:
                           self._handlers.register(key, object)
                   res[key] = object
        return res

    def modules(self, name=""):
        """ return a list of modules in the named packages or cfg.packages if no module name is provided. """
        from botlib.space import cfg
        if not name:
            names = cfg.packages
        else:
            names = [name, ]
        for name in names:
            package = self.direct(name)
            for pkg in pkgutil.walk_packages(package.__path__, name + "."):
                yield pkg[1]

    def once(self, txt):
        """ run once command. """
        try:
            e = self.cmnd(txt)
            self.dispatch(e)
            return e
        except:
            print(get_exception())

    def put(self, *args, **kwargs):
        if args:
            logging.debug(args[0])
        super().put(*args, **kwargs)

    def register(self, key, value, force=True):
        """ register handlers. """
        self._handlers.register(key, value, force)

    def reload(self, name, force=False, event=None):
        """ reload module. """
        e = event or template.get("event")
        try:
            self._table[name].shutdown(e)
        except (KeyError, AttributeError):
            pass
        self.loading(name, force)
        if force:
            try:
                self._table[name].init(e)
            except (KeyError, AttributeError):
                pass
        if name in self._table:
            return self._table[name]

    def shutdown(self, close=False, write=True):
        """ stop bot, services and plugins. """
        from .space import cfg, fleet, kernel, partyline, runtime
        self.clear()
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

    def walk(self, name, init=False, force=False):
        """ return all modules in a package. """
        mod = []
        logging.info("! walk %s" % name)
        for modname in sorted(list(self.modules(name))):
            try:
                self.loading(modname, force)
                if init:
                    self.init(modname)
                mod.append(modname)
            except Exception as ex:
                logging.error(get_exception())
                continue
        return mod
