# BOTLIB - Framework to program bots.
#
# Copyright (C) 2016,2017 by Bart Thate <bthate@dds.nl>
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

def init(event):
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
