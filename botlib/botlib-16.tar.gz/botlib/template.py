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

""" cfg objects containing default values for various services and plugins. """

from .object import Object
from .event import Event

import os
import time

xmpp = Object()
xmpp.user = "monitor@localhost"
xmpp.server = "localhost"
xmpp.username = "monitor"
xmpp.channel = "#botlib"
xmpp.nick = "monitor"
xmpp.cfg = "xmpp"
xmpp.port = 5222
xmpp.owner = ""
xmpp.openfire = False
xmpp.noresolver = False
xmpp.silent = False

irc = Object()
irc.cfg = "irc"
irc.channel = "#botlib"
irc.encoding = "utf-8"
irc.nick = "botlib"
irc.ipv6 = False
irc.owner = ""
irc.port = 6667
irc.realname = "botlib"
irc.server = "localhost"
irc.servermodes = ""
irc.username = "botlib"
irc.ssl = False
irc.silent = False

kernel = Object()
kernel.all = False
kernel.args = []
kernel.cfg = "kernel"
kernel.changed = False
kernel.automeet = True
kernel.banner = False
kernel.exclude = "test,xmpp"
kernel.homedir = os.path.abspath(os.path.expanduser("~"))
kernel.hostname = "localhost"
kernel.homedirs = False
kernel.ignore = []
kernel.init = ""
kernel.local = True
kernel.logdir = os.path.join(kernel.homedir, ".botlog")
kernel.loglevel = ""
kernel.owner = "root@shell"
kernel.match = ""
kernel.mods = ""
kernel.modules = []
kernel.needed = ["botlib.clock"]
kernel.packages = ["botlib"]
kernel.port = 10102
kernel.shell = False
kernel.scan = False
kernel.resume = False
kernel.reboot = False
kernel.tailfile = ""
kernel.txt = "Framework to program bots"
kernel.test = False
kernel.verbose = False
kernel.watch = ""
kernel.workdir = ""
kernel.write = False

udp = Object()
udp.cfg = "udp"
udp.host = "localhost"
udp.port = 5500
udp.password = "boh"
udp.seed = "blablablablablaz" # needs to be 16 chars wide
udp.server = udp.host
udp.owner = ""

rest = Object()
rest.cfg = "rest"
rest.hostname = "localhost"
rest.port = 10102
rest.server = rest.hostname
rest.owner = ""

stats = Object()
stats.cfg = "stats"
stats.showurl = True
stats.owner = ""

rss = Object()
rss.cfg = "rss"
rss.save_list = []
rss.display_list = ["title", "link", "published"]
rss.descriptions = ["officiel", ]
rss.sleeptime = 600
rss.ignore = []
rss.dosave = []
rss.nosave = []
rss.showurl = False
rss.owner = ""

cli = Object()
cli.welcome = "mogge!!"
cli.cfg = "cli"
cli.server = "localhost"
cli.owner = ""
cli.silent = False

input = Object()
input.server = "localhost"
input.cfg = "input"
input.owner = "root@shell"
input.silent = True

result = Object()
result.server = "localhost"
result.cfg = "input"
result.owner = "root@shell"

testbot = Object()
testbot.server = "localhost"
testbot.cfg = "input"
testbot.owner = "root@shell"
testbot.channel = "#botlib"

raw = Object()
raw.server = "localhost"
raw.cfg = "raw"
raw.owner = "root@shell"
raw.channel = "#botlib"

bot = Object()
bot.server = "localhost"
bot.cfg = "bot"
bot.owner = "root@shell"
bot.channel = "#botlib"

timer = Object()
timer.cfg = "timer"
timer.latest = 0

default = Object()
default.cfg = "default"

template = Object()
template.xmpp = xmpp
template.irc = irc
template.kernel = kernel
template.udp = udp
template.rest = rest
template.rss = rss
template.cli = cli
template.input = input
template.result = result
template.testbot = testbot
template.bot = bot
template.default = default
template.timer = timer
template.raw = raw
template.stats = stats

def test(event):
    event.reply("yo!")

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
varnames.seconds = 60
varnames.daystr = "Sat Jan 14 00:02:29 2017"
varnames.txt = "i told you so !!"
varnames.path = "data/runtime/kernel"
varnames.optionlist = "-b -a -l info"
varnames.level = "info"
varnames.error = "info"
varnames.fd = 1
varnames.event = Event()
#varnames.old = termios.tcgetattr(1)
varnames.text = "blablabla mekker"
varnames.signature = "1e7f50d2015ac2ddc1f2ae8cf8ed6dfd896cab71"
varnames.u = "bart!~bart@localhost"
varnames.jid = "monitor@localhost/blamekker"
varnames.url = "http://localhost"
varnames.obj = Object(txt="version")
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
