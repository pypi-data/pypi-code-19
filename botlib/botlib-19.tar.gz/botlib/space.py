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

""" central module to store objects in. """

__all__ = ["alias", "db", "cfg", "exceptions", "fleet", "kernel", "launcher", "partyline", "runtime", "seen", "users"]

from .db import Db
from .fleet import Fleet
from .kernel import Kernel
from .launcher import Launcher
from .object import Config, Object
from .register import Register
from .template import template
from .users import Users

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
    """ load basic objects (alias, seen and users). """
    alias.load(os.path.join(cfg.workdir, "runtime", "alias"))
    alias.l = "cmnds"
    alias.v = "version"
    alias.f = "find"
    seen.load(os.path.join(cfg.workdir, "runtime", "seen"))
    users.load(os.path.join(cfg.workdir, "runtime", "users"))
