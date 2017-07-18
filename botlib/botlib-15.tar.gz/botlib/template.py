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

import os

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

opts_defs = [
    ('-a', '--all', 'store_true', False, 'all', "load all plugins."),
    ('-b', '--banner', 'store_true', False, 'banner', "show banner"),
    ("-c", "--copy", "string", "", "copyfrom", "copy data from origin into this working directory"),
    ('-d', '--workdir', 'string', "", 'workdir', "working directory."),
    ('-e', '--onerror', 'store_true', False, 'onerror', "raise on error."),
    ('-f', '--filelog', "string", "", "filelog", "enable logging to file."),
    ('-i', '--init', 'string', "", 'init', "whether to initialize plugins."),
    ('-l', '--loglevel', 'string', "", 'loglevel', "loglevel."),
    ('-m', '--mods', 'string', "", 'mods', "modules to load."),
    ('-o', '--owner', 'string', "root@shell", 'owner', "userhost/JID of the bot owner."),
    ('-p', '--port', 'string', 10102, 'port', "port to run HTTP server on."),
    ('-r', '--resume', 'store_true', False, 'resume', "resume on restart."),
    ('-s', '--shell', 'store_true', False, 'shell', "start a shell."),
    ('-t', '--test', 'store_true', False, 'test', "switch to test mode"),
    ("-u", "--user", "store_true", False, "user", "use given user profile"),
    ('-v', '--verbose', 'store_true', False, 'verbose', 'use verbose mode.'),
    ('-w', '--write', 'store_true', False, 'write', 'save kernel state after boot.'),
    ('-x', '--exclude', 'string', "test", 'exclude', "modules to exclude."),
    ('-y', '--yes', 'store_true', False, 'yes', "enable all boot options."),
    ('-z', '--reboot', 'store_true', False, 'reboot', "enable rebooting."),
    ('-6', '--use_ipv6', 'store_true', False, 'use_ipv6', 'enable ipv6'),
    ('', '--local', 'store_true', False, 'local', "use cuurent directory as the work directory."),
    ('', '--no_certs', 'store_true', False, 'no_certs', "disables XMPP certificates."),
    ('', '--homedir', 'string', os.path.expanduser("~"), 'homedir', "user's homedir."),
    ('', '--daemon', 'store_true', False, 'daemon', "switch to daemon mode."),
    ('', '--debug', 'store_true', False, 'debug', "enable debug mode.")
]

opts_defs_sed = [
    ('-d', '--dir', 'string', "", 'dir_sed', "directory to work with."),
    ('-l', '--loglevel', 'string', "error", 'loglevel', "loglevel"),
]

opts_defs_udp = [
    ('-p', '--port', 'string', "10102", 'port', "port to run API server on"),
    ('-l', '--loglevel', 'string', "error", 'loglevel', "loglevel"),
]

opts_defs_doctest = [
    ('-e', '--onerror', 'store_true', False, 'onerror', "raise on error"),
    ('-v', '--verbose', 'store_true', False, 'verbose', "use verbose"),
    ('-l', '--loglevel', 'string', "error", 'loglevel', "loglevel"),
]
