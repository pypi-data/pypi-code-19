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

""" watch files. """

from .clock import Repeater
from .object import Object
from .engine import Engine
from .space import cfg, db, launcher, partyline, runtime
from .trace import get_exception

import logging
import select
import time
import io
import os

def init(*args, **kwargs):
    watcher = Watcher()
    launcher.launch(watcher.start)
    return watcher

def out(txt):
    for orig, sockets in partyline.items():
        for sock in sockets:
            sock.write(str(txt, "utf-8"))
            sock.flush()

class Watcher(Object):

    def start(self):
        watchers = []
        for fn in self.watchlist():
            try:
                reader = open(fn, "r")
                reader.seek(0, 2)
                fd = reader.fileno()
                watchers.append(fd) 
            except FileNotFoundError as ex:
                logging.info("! not watching %s" % fn)
        for w in watchers:
            logging.info("! watcher on %s" % w)
        while 1:
            time.sleep(1.0)
            (i, o, e) = select.select(watchers,[],[])
            for fd in i:
                try:
                    txt = os.read(fd, 1024)
                    out(txt)
                except:
                    logging.error(get_exception())

    def watchlist(self):
        w = list([x.watch for x in db.find("watch")])
        if cfg.watch:
            w.append(cfg.watch)
        return w
# BOTLIB - Framework to program bots
#
# LICENSE
#
# this file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands
