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

""" central module to store objects in. """

__all__ = ["alias", "db", "cfg", "exceptions", "fleet", "kernel", "launcher", "partyline", "runtime", "seen", "users"]

from .db import Db
from .error import *
from .fleet import Fleet
from .kernel import Kernel
from .launcher import Launcher
from .object import Config, Default, Object
from .register import Register
from .users import Users
from .utils import reset

import os.path

alias = Object()
db = Db()
cfg = Config()
exceptions = []
fleet = Fleet()
kernel = Kernel()
launcher = Launcher()
partyline = Register()
runtime = Register()
seen = Object(urls=[])
users = Users()

def load():
    alias.load(os.path.join(cfg.bootdir, "runtime", "alias"))
    alias.l = "cmnds"
    alias.v = "version"
    alias.f = "find"
    seen.load(os.path.join(cfg.bootdir, "runtime", "seen"))
    users.load(os.path.join(cfg.bootdir, "runtime", "users"))
