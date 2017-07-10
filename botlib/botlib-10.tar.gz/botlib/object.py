# botlib/object.py
#
#

""" JSON file backed objectect with dotted access.  """

from .error import ENOJSON
from .utils import *

import threading
import datetime
import _thread
import hashlib
import logging
import string
import atexit
import types
import fcntl
import time
import json
import tty
import sys
import os

class Object(dict):

    """
        Dict with dotted access instead of brackets, with json files to sync and load from.

    """

    def __init__(self, *args, **kwargs):
        """ Construct an Object, dotted dictionairy access instead of brackets. """
        super().__init__(*args, **kwargs)
        #self.update(kwargs)
        
    def __getattribute__(self, name):
        """
            Get attribute and if fail check item access.

        """
        if name == "_path":
            from botlib.space import cfg
            p = os.path.join(cfg.workdir, sname(self).lower())
            return p
        if name == "url":
            return urled(self)
        if name == "type":
            return sname(self).lower()
        if name == "_type":
            return str(type(self))
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)

    def __getattr__(self, name):
        """
            | Get missing attribute by name. initialize into an Object if if name is missing from dictionary.
            | Predefined names are _ready and counter. _ready is for waiting on results and counter is for integer simulation. 

        """ 
        if name == "_connected":
            self._connected = Object()
        if name == "_container":
            self._container = Default()
        if name == "_counter":
            self._counter = Default(default=0)
        if name == "_error":
            self._error = Default()
        if name == "_funcs":
            self._funcs = []
        if name == "_ready":
            self._ready = threading.Event()
        if name == "_state":
            self._state = Object()
        if name == "_thrs":
            self._thrs = []
        if name == "_time":
            self._time = Default(default=0.0)
        if name == "cfg":
            self.cfg = Config().template(self.type)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __iadd__(self, name, value):
        self[name] += value
        return self[name]

    def __repr__(self):
        """ Return module.class as a class type. """
        return '<%s.%s at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def __setattr__(self, name, value):
        """ Implement dotted dict access. """
        return self.__setitem__(name, value)

    def __str__(self):
        """ Return a prettified json string. """            
        return self.nice()

    def grep(self, val):
        """ Grep for a matching stringified value, return a Object with those matching values. """
        o = Object()
        for key, value in self.items():
            if val in str(value) and value not in o:
                o[key] = value
        return o

    def id(self, *args, **kwargs):
        return sname(self).lower()

    def load(self, path, force=False, skip=[], full=True):
        """ Load a json file into this object. use skip as a list of keys to skip. """
        path = os.path.abspath(path)
        logging.debug("# load %s" % path)
        ondisk = self.read(path)
        self._container.path = path
        fromdisk = json.loads(ondisk)
        if "signature" in fromdisk:
            if not verify_signature(fromdisk["data"], fromdisk["signature"]) and not force:
                logging.warn("# signature mismatch %s" % path)
        if "data" in fromdisk:
            self.update(slice(fromdisk["data"], skip=skip, full=full))
            self._container.update(slice(fromdisk, skip=["data"]))
        return self

    def last(self, *args, **kwargs):
        from botlib.space import kernel
        d = kernel.last(sname(self).lower())
        if d:
            self.update(d)
        return self

    def loads(self, s):
        """ Update with deconstructed (dict) json string. """
        self.update(json.loads(s))

    def merge(self, object):
        for k, v in object.items():
            if v:
                self[k] = v

    def nice(self, *args, **kwargs):
        """ Return a nicyfied, indent=4, sort_key is True, json dump. """
        return json.dumps(self, default=smooth, indent=4, sort_keys=True)

    def pure(self, *args, **kwargs):
        """ Return a sliced (no _ keys), indent=4, sort_key is True, json dump. """
        return dumps(slice(self, full=False), indent=4, sort_keys=True)

    def prepare(self):
        """
            | Prepare the object and return a string containing the "data" part.
            | Keyword can be "prefix" when using a subdirectory.
            | Use "saved" when savestamp need to be different from the "now" timestamp.

        """
        import time
        todisk = Object()
        todisk.data = dumped(slice(self, skip=["_container", "_parsed"], full=True))
        todisk.data._type = str(type(self))
        if "prefix" not in todisk:
            todisk.prefix = sname(self).lower()
        if "saved" not in todisk:
            todisk.saved = time.ctime(time.time())
        try:
            todisk.signature = make_signature(todisk["data"])
        except:
            pass
        try:
            result = json.dumps(todisk, default=smooth, indent=4, ensure_ascii=False, sort_keys=True)
        except TypeError:
            raise ENOJSON
        return result

    def printable(self, keys=[], skip=[], nokeys=False):
        """ Determine from provided keys list and/or from skipping from a skiplist a displayable string from those attributes. """
        keys = keys or self.keys()
        result = []
        for key in keys:
             if key == "default":
                 continue
             if key.startswith("_"):
                 continue
             if key in skip:
                 continue
             if nokeys:
                 result.append("%4s" % str(self[key]))
             else:
                 result.append("%-6s%-6s" % (key, self[key]))
        txt = " ".join(reversed(sorted(result)))
        return txt.rstrip()

    def read(self, path):
        """ Read a json dump from given path, returning the json string with comments stripped. """
        try:
            f = open(path, "r", encoding="utf-8")
        except FileNotFoundError:
            return "{}"
        res = ""
        for line in f:
            if not line.strip().startswith("#"):
                res += line
        if not res.strip():
            return "{}"
        f.close()
        return res

    def register(self, key, val, force=False):
        """ Register key, value and throw an exception is value is already set. """
        if key in self and not force:
            raise bot.error.ESET(key)
        self[key] = val   

    def save(self, stime=""):
        """ save a static (fix filepath) version of this object. """
        return self.sync(stime=stime)

    def search(self, name):
        """ Search this objects keys skipping keys that start with "_". """
        o = Object()
        for key, value in self.items():
            if key.startswith("_"):
                continue
            if key in name:
                o[key] = value
            elif name in key.split(".")[-1]:
                o[key] = value
        return o

    @locked
    def sync(self, path="", stime=""):
        """ Sync to disk using provided/created path. Optionally a path can be provided. """
        from botlib.space import cfg, kernel, EBORDER
        if not path:
            path = get_path(self)
        if not path:
            path = self._path
            if stime:
                path = os.path.join(path, stime)
            else:
                path = os.path.join(path, rtime())
        path = os.path.abspath(os.path.normpath(path))
        logging.info("! sync %s" % path)
        if not (cfg.workdir in path or cfg.bootdir in path):
            raise EBORDER(path)
        self._container.path = path
        d, fn = os.path.split(path)
        cdir(d)
        todisk = self.prepare()
        rpath = path + "_tmp"
        datafile = open(rpath, 'w')
        fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        datafile.write(headertxt % "%s characters" % len(todisk))
        datafile.write(todisk)
        datafile.write("\n")
        datafile.flush()
        os.rename(rpath, path)
        fcntl.flock(datafile, fcntl.LOCK_UN)
        datafile.close()
        return path

    def clear(self):
        """ Clear the ready flag. """
        self._ready.clear()

    def isSet(self):
        """ Check whether ready flag is set. """
        return self._ready.isSet()

    def ready(self):
        """ Signal this object as "ready". """
        self._ready.set()

    def wait(self, sec=None):
        """ Wait for this object's ready flag. """
        self._ready.wait(sec)
        for thr in self._thrs:
            thr.join()

class Default(Object):

    """
        A object with a "default" set. Standard default return is Object().

    """

    def __init__(self, *args, **kwargs):
        """ Constructor that initializes a variable with Object() as a default. """
        super().__init__(*args, **kwargs)
        self.default = 0

    def __getattr__(self, name):
        """ Override Object.__getattr__.  """ 
        try:
            return super().__getattr__(name)
        except AttributeError as ex:
            self[name] = self.default
        return self[name]

class Config(Default):

    """
        A Config objectect can read previous cfg from disk.

    """

    default = ""

    def template(self, name):
        from botlib.template import template
        self.update(template.get(name, {}))
        return self

    def fromdisk(self, name):
        from botlib.space import cfg
        self.template(name)
        self.load(os.path.join(cfg.workdir, "config", name))
        return self

def slice(object, keys=[], skip=[], full=False):
    """ return a slice of an object. """
    o = Object()
    if not keys:
        keys = object.keys()
    for key in keys:
        if key in skip:
            continue
        if not full and key.startswith("_"):
            continue
        val = object.get(key, None)
        if val and "keys" in dir(val):
            o[key] = slice(val)
        else:
            o[key] = val
    return o

def dumped(o):
    if "items" not in dir(o):
        return o
    if type(o) == dict:
        o = Object(o)
    o._type = str(type(o))
    for k, v in o.items():
        if k == "_type":
            continue
        if type(v) in nodict_types:
            o[k] = v
        else:
            o[k] = dumped(v)
    return o
