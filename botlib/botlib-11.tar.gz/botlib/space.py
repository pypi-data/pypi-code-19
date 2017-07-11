# botlib/space.py
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
