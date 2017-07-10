# botlib/space.py
#
#

""" Framework to program bot, JSON file backend, MIT license. """

__all__ = ["exceptions", "alias", "cfg", "fleet", "kernel", "runtime", "seen", "users"]

from botlib.db import Db
from botlib.error import *
from botlib.fleet import Fleet
from botlib.kernel import Kernel
from botlib.launcher import Launcher
from botlib.object import Config, Default, Object
from botlib.register import Register
from botlib.users import Users

from .utils import reset

import os.path

#:
exceptions = []
#:
alias = Object()
#:
db = Db()
#:
cfg = Config()
#:
fleet = Fleet()
#:
kernel = Kernel()
#:
launcher = Launcher()
#:
partyline = Register()
#:
runtime = Register()
#:
seen = Object(urls=[])

#:
users = Users()

def load():
    alias.load(os.path.join(cfg.bootdir, "runtime", "alias"))
    alias.l = "cmnds"
    alias.v = "version"
    alias.f = "find"
    seen.load(os.path.join(cfg.bootdir, "runtime", "seen"))
    users.load(os.path.join(cfg.bootdir, "runtime", "users"))
