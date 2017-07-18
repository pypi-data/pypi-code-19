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

""" JSON file db. """

from .event import Event
from .object import Default, Object
from .utils import root, elapsed, fn_time

import logging
import time
import os

class Db(Object):

    """ database object managing JSON files. """

    def scan(self, path, *args, **kwargs):
        """ scan all files. """
        p = Default(kwargs, default="")
        if not path.endswith(os.sep):
            path += os.sep
        result = []
        for rootdir, dirs, files in os.walk(path, topdown=True):
            if not os.path.isdir(rootdir):
                continue
            for fn in files:
                fnn = os.path.join(rootdir, fn)
                timed = fn_time(fnn)
                if timed and p.start and timed < p.start:
                    continue
                if timed and p.end and timed > p.end:
                    continue
                yield fnn

    def find(self, prefix, *args, **kwargs):
        """ find all objects stored with a prefix subdirectory. """
        for fn in self.prefixed(prefix, *args):
            try:
                obj = Object().load(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            if "deleted" in obj and obj.deleted:
                continue
            yield obj

    def prefixed(self, *args, **kwargs):
        """ return all filename in a workdir subdirectory, the 'prefix'. """
        from .space import cfg
        if not args:
            return []
        files = []
        if cfg.workdirs:
            workdirs = cfg.workdirs
        else:
            workdirs = [root()]
        for workdir in workdirs:
            path = os.path.join(workdir, args[0])
            if not os.path.exists(path):
                continue
            for fn in self.scan(path, *args, **kwargs):
                files.append(fn)
        return sorted(files, key=lambda x: fn_time(x))

    def prefixes(self):
        """ show prefixs (toplevel directories) in the workdir. """
        for p in os.listdir(root()):
            yield p

    def is_prefix(self, prefix):
        """ chech whether prefix (subdirectory in the workdir) exists. """
        for p in os.listdir(root()):
            if prefix in p:
                return True

    def selected(self, event):
        """ select objects based on a _parsed event. """
        thrs = []
        if not event._parsed.args:
            return []
        starttime = time.time()
        nr = -1
        index = event._parsed.index
        for fn in self.prefixed(*event._parsed.args, **event._parsed):
            obj = self.selector(event, fn)
            if obj:
                nr += 1
                if index != None and nr != index:
                    continue
                yield obj
        endtime = time.time()
        logging.info("! selected %s %s" % (nr + 1, elapsed(endtime - starttime, short=False)))

    def selector(self, event, fn, obj=None):
        """ select objects matching the _parsed fields in the event object. """
        import botlib.selector
        s = botlib.selector
        if not obj:
            obj = Object().load(fn)
        if "nodel" not in event and "deleted" in obj and obj.deleted:
            return
        if not s.selector(obj, event._parsed.fields):
            return
        if s.notwanted(obj, event._parsed.notwant):
            return
        if not s.wanted(obj, event._parsed.want):
            return
        if s.ignore(obj, event._parsed.ignore):
            return
        if s.uniq(obj, event._parsed.uniq):
            return
        return obj

    def sequence(self, prefix, start, end=time.time(), skip=[]):
        """ select objects of type prefix, start time till end time. """
        p = Object()
        p.start = start
        p.end = end
        for fn in self.prefixed(prefix, **p):
            do_skip = False
            for k in skip:
                if k in fn:
                    do_skip = True
            if do_skip:
                continue
            try:
                e = Event().load(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            yield e

    def since(self, start, *args, **kwargs):
        """ return all objects since a given time. """
        e = Event(**kwargs)
        e.start = start
        for fn in self.prefixed(*args, **e):
            try:
                obj = Object().load(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            if "deleted" in obj and obj.deleted:
                continue
            yield obj

    def first(self, *args, **kwargs):
        """ return first object matching provided prefix. """
        for fn in self.prefixed(*args, **kwargs):
            try:
                obj = Object().load(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            if "deleted" in obj and obj.deleted:
                continue
            if len(args) > 1 and obj.get(args[0]) != args[1]:
                continue
            return obj

    def last(self, *args, **kwargs):
        """ return last record with a matching prefix. """
        prefix = args[0]
        if len(args) > 1:
            value = args[1]
        else:
            value = ""
        for fn in self.prefixed(args[0], **kwargs)[::-1]:
            try:
                obj = Object().load(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            if "deleted" in obj and obj.deleted:
                continue
            if value and obj.get(prefix, "") != value:
                continue
            return obj
