# botlib/test.py
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

""" plugin containing test commands and classes. """

from .object import Object
from .event import Event
from .utils import stripped, sname
from .trace import get_exception
from .error import ENODATE
from .space import cfg, fleet, kernel, users
from .template import opts_defs

import logging
import termios
import string
import random
import types
import time
import os

def test():
    print("yooo!")

testdict = {
               "key1": "val1",
               "key2": "val2"
           }

options = ["test", 1, 10, "mekker", True, False, 33.33, testdict]

examples = Object()
examples.find = "find todo"
examples.last = "last cfg"
examples.tommorrow = "tomorrow take some time off."
examples.deleted = "deleted rss"
examples.log = "log wakker"
examples.rss = "http://nos.nl"
examples.todo = "todo code some code"
examples.user = "user root@shell"
examples.timer = "timer 23.35 blablabla"
examples.show = "show fleet"
examples.shop = "shop bacon"
examples.rm = "rm rss[0]"
examples.restore = "restore rss[0]"
examples.reload = "reload cmnds"
examples.perm = "perm root@shell oper"
examples.meet = "meet root@shell oper"
examples.mbox = "mbox ~/25-1-2013"
examples.loglevel = "loglevel info"
examples.first = "first cfg"
examples.dump = "dump todo"
examples.delperm = "delperm root@shell oper"
examples.cfg = "cfg irc"
examples.announce = "announce bla"
examples.alias = "alias l cmnds"

varnames = Object()
varnames.object = Object(txt="test", date="Sat Jan 14 00:02:29 2017")
varnames.daystring = "2017-08-29 16:34:23.837288"
varnames.event = Event(txt="test")
varnames.seconds = 60
varnames.daystr = "Sat Jan 14 00:02:29 2017"
varnames.txt = "i told you so !!"
varnames.path = "data/runtime/kernel"
varnames.optionlist = "-b -a -l info"
varnames.level = "info"
varnames.error = "userdefined error message"
varnames.fd = 1
#varnames.old = termios.tcgetattr(1)
varnames.text = "blablabla mekker"
varnames.signature = "1e7f50d2015ac2ddc1f2ae8cf8ed6dfd896cab71"
varnames.options = opts_defs
varnames.u = "bart!~bart@localhost"
varnames.jid = "monitor@localhost/blamekker"
varnames.url = "http://localhost"
varnames.obj = {"bla": "mekker"}
varnames.func = test
varnames.timestamp = time.time()
varnames.origin = "root@shell"
varnames.perm = "OPER"
varnames.o = Object(txt="test")
varnames.depth = 2
varnames.keys = ["test", "txt"]
varnames.uniqs = ["bla"]
varnames.ignore = {"test": "mekker"}
varnames.notwant = {"test": "mekker"}
varnames.want = {"test": "mekker"}

def randomname():
    return random.choice(options)

def randomarg():
    t = random.choice(types.__all__)
    return types.new_class(t)()
    
def e(event):
    event.reply(event.nice())
    event.save()

def flood(event):
    txt = "b" * 5000
    event.reply(txt)

def forced(event):
    for bot in fleet:
        try:
            bot._sock.shutdown(2)
        except (OSError, AttributeError):
            pass 

if not cfg.test:
    def exception(event):
        if not users.allowed(event.origin, "OPER"):
            event.reply("you are not allowed to give the exception command.")
            return
        raise Exception('test exception')

def wrongxml(event):
    event.reply('sending bork xml')
    for bot in fleet:
        bot.raw('<message asdfadf/>')

def unicode(event):
    event.reply(outtxt)

def deadline(event):
    try:
        nrseconds = int(event.parsed.rest)
    except:
        nrseconds = 2
    event.reply('starting %s sec sleep' % nrseconds)
    time.sleep(nrseconds)

def testcfg(event):
    e = Event()
    path = e.save()
    event.reply(path)

def html(event):
    event.reply('<span style="font-family: fixed; font-size: 10pt"><b>YOOOO BROEDERS</b></span>')

def cmndrun(event):
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    for name in sorted(kernel.modules()):
        if name in ["botlib.test", "botlib.rss"]:
            continue
        mod = kernel.direct(name)
        for n in dir(mod):
           if n in exclude:
               continue
           func = getattr(mod, n, None)
           if func and type(func) in [types.FunctionType, types.MethodType]:
               if "event" in func.__code__.co_varnames:
                   e = Event()
                   e._funcs.append(func)
                   e.origin = "root@shell"
                   e.server = "localhost"
                   e.btype = "cli"
                   kernel.put(e)

def functest(event):
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    for name in sorted(kernel.modules()):
        if name in ["botlib.test", "botlib.rss"]:
            continue
        mod = kernel.direct(name)
        keys = dir(mod)
        random.shuffle(keys)
        for n in keys:
           if n in exclude:
               continue
           obj = getattr(mod, n, None)
           for func in dir(obj):
               if  func and type(func) in [types.FunctionType, types.MethodType]:
                   arglist = []
                   for name in func.__code__.co_varnames:
                       nrvar = func.__code__.co_argcount
                       n = varnames.get(name, None)
                       if n:
                           arglist.append(n)
                   try:
                       func(*arglist[:nrvar])
                   except:
                       logging.error(get_exception())
               
def testcmnds(event):
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    keys = list(kernel._names.keys())
    random.shuffle(keys)
    for cmnd in keys:
        if cmnd in exclude:
            continue
        if cmnd == "find":
            name = "email"
        else:
            name = randomname()
        e = Event(event)
        e.btype = event.btype
        e.server = event.server
        cmnd = examples.get(cmnd, cmnd)
        e.txt = cmnd
        e.origin = "root@shell"
        e.parse()
        kernel.put(e)

def runkernel(event):
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    event.origin = "root@shell"
    thrs = []
    try:
        nrloops = int(event._parsed.args[0])
    except:
        nrloops = 1
    for x in range(nrloops):
        thr = kernel.launch(testcmnds, event)
        thrs.append(thr)
    for thr in thrs:
        thr.join()

exclude = ["reboot", "real_reboot", "fetcher", "synchronize", "init", "shutdown", "wrongxml","mbox", "testcmnds", "runkernel", "functest", "cmndrun"]
outtxt = u"Đíť ìš éèñ ëņċøďıńğŧęŝţ· .. にほんごがはなせません .. ₀0⁰₁1¹₂2²₃3³₄4⁴₅5⁵₆6⁶₇7⁷₈8⁸₉9⁹ .. ▁▂▃▄▅▆▇▉▇▆▅▄▃▂▁ .. .. uǝʌoqǝʇsɹǝpuo pɐdı ǝɾ ʇpnoɥ ǝɾ"
