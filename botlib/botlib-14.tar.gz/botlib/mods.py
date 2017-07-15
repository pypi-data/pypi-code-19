# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" program boot and module loading. """

from .event import Event
from .object import Object
from .register import Register
from .utils import set_completer

import importlib
import logging
import pkgutil
import types
import os

class Mods(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cmnds = []
        self._handlers = Register()
        self._names = Register()
        self._table = Object()
     
    def direct(self, name, package=None):
        """ import a module directly, not storing it in the cache. """
        return importlib.import_module(name, package)

    def get_handlers(self, cmnd):
        """ search for a function registered by command. """
        from .space import alias, launcher
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
                    logging.warn("# module %s" % modname)
                    self.loading(modname)
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
            mod = self.load_mod(modname)
        if mod and "init" in dir(mod):
            thr = launcher.launch(mod.init, event, name="%s.init" % n)
            return thr

    def initialize(self):
        from .space import cfg, load
        if not self._names and not cfg.write:
            m = Mods().load(os.path.join(cfg.bootdir, "runtime", "mods"))
            self._names.update(m._names)
        if not self._names:
            self.walk("botlib", True)
            if cfg.write:
                self.sync(os.path.join(cfg.bootdir, "runtime", "mods"))
        if not self._cmnds:
            self._cmnds = sorted(set([cmnd for cmnd in self._names.keys()]))
        set_completer(self._cmnds)
        load()

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
        mod = self.direct(modname, force)
        res = Object()
        for key in dir(mod):
            if key.startswith("_"):
                continue
            object = getattr(mod, key, None)
            if object and type(object) == types.FunctionType:
                if "event" in object.__code__.co_varnames:
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

    def reload(self, name, force=False, event=None):
        """ reload module. """
        e = event or Event()
        if name not in self._table:
            return
        self._table[name].shutdown(e)
        self.loading(name, force)
        if force:
            self._table[name].init(e)
        if name in self._table:
            return self._table[name]

    def walk(self, name, init=False, force=False):
        """ return all modules in a package. """
        logging.info("! walk %s" % name)
        for modname in sorted(list(self.modules(name))):
            self.loading(modname, force)
            if init:
                self.init(modname)
