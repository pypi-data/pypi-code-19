# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" central module to store objects in. """

__all__ = ["alias", "db", "cfg", "exceptions", "fleet", "kernel", "launcher", "partyline", "runtime", "seen", "users"]

from .db import Db
from .error import *
from .fleet import Fleet
from .kernel import Kernel
from .launcher import Launcher
from .object import Config, Default, Object
from .register import Register
from .template import template
from .users import Users
from .utils import reset

import os.path

alias = Object()
db = Db()
cfg = Config(template.get("kernel"))
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
