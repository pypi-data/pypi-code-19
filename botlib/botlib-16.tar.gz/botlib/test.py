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

""" plugin containing test commands and classes. """

from .object import Object
from .event import Event
from .utils import stripped, sname
from .trace import get_exception
from .error import ENODATE
from .space import cfg, fleet, kernel, launcher, users
from .options import opts_defs
from .template import varnames, examples

import logging
import termios
import string
import random
import types
import time
import os

exclude = ["funcs", "reboot", "real_reboot", "fetcher", "synchronize", "init", "shutdown", "wrongxml","tests"]
outtxt = u"Đíť ìš éèñ ëņċøďıńğŧęŝţ· .. にほんごがはなせません .. ₀0⁰₁1¹₂2²₃3³₄4⁴₅5⁵₆6⁶₇7⁷₈8⁸₉9⁹ .. ▁▂▃▄▅▆▇▉▇▆▅▄▃▂▁ .. .. uǝʌoqǝʇsɹǝpuo pɐdı ǝɾ ʇpnoɥ ǝɾ"

def test():
    print("yooo!")

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
        nrseconds = int(event._parsed.rest)
    except:
        nrseconds = 10
    event.direct('starting %s sec sleep' % nrseconds)
    time.sleep(nrseconds)

deadline._threaded = True

def testcfg(event):
    e = Event()
    path = e.save()
    event.reply(path)

def html(event):
    event.reply('<span style="font-family: fixed; font-size: 10pt"><b>YOOOO BROEDERS</b></span>')

def tests(event):
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    events = []
    try:
        nr = int(event._parsed.rest)
    except ValueError:
        nr = 10
    for x in range(nr):
        keys = list(kernel.list("botlib"))
        random.shuffle(keys)
        for cmnd in keys:
            if cmnd in exclude:
                continue
            if cmnd == "find":
                name = "email From"
            else:
                name = varnames.get(cmnd, "From")
            e = Event(event)
            e.btype = event.btype
            e.server = event.server
            cmnd = "%s %s" % (cmnd, name)
            e.txt = cmnd
            e.origin = "root@shell"
            kernel.put(e)
            events.append(e)
    for e in events:
        e.wait()

tests._threaded = True

def dofunc(func):
    e = Event()
    if func and type(func) in [types.FunctionType, types.MethodType]:
        arglist = []
        nrvar = func.__code__.co_argcount
        for name in func.__code__.co_varnames:
            n = varnames.get(name, None)
            if n:
                arglist.append(n)
            else:
                arglist.append(e)
            logging.info("! funcs %s %s" % (func, ",".join([str(x) for x in arglist])))
            try:
                func(*arglist[:nrvar])
            except:
                logging.error(get_exception())

def funcs(event):
    if not cfg.changed:
        event.reply("you need to set the workdir, use the -d option")
        return
    if not cfg.test:
        event.reply("the test option is not set.")
        return
    for name in sorted(kernel.modules("botlib")):
        mod = kernel.load(name)
        keys = dir(mod)
        random.shuffle(keys)
        for key in keys:
           if "_" in key:
               continue
           if key in exclude:
               continue
           obj = getattr(mod, key, None)
           dofunc(obj)
           for nkey in dir(obj):
               o = getattr(obj, nkey, None)
               if o:
                   dofunc(o)

funcs._threaded = True
