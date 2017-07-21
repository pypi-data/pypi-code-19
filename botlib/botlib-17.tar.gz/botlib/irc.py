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

""" IRC bot class. """

from .bot import Bot
from .compose import compose
from .event import Event
from .fleet import Fleet
from .register import Register
from .error import EDISCONNECT
from .object import Object
from .space import cfg, fleet, kernel, launcher, partyline
from .utils import split_txt

from botlib import __version__

import logging
import _thread
import random
import socket
import queue
import time
import ssl
import re
import os

def init(*args, **kwargs):
    """ initialise a IRC bot. """
    bot = IRC()
    bot.start()
    return bot

def stop(event):
    """ stop all IRC bots. """
    for bot in fleet.get_type("irc"):
        bot.stop()

class IRC(Bot):

    """ Bot to connect to IRC networks. """

    cc = "!"
    default = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer = []
        self._handlers.register("004", self.connected)
        self._handlers.register("005", self.h005)
        self._handlers.register("ERROR", self.errored)
        self._handlers.register("352", self.h352)
        self._handlers.register("353", self.h353)
        self._handlers.register("366", self.h366)
        self._handlers.register("433", self.h433)
        self._handlers.register("513", self.h513)
        self._handlers.register("PING", self.pinged)
        self._handlers.register("PONG", self.ponged)
        self._handlers.register("QUIT", self.quited)
        self._handlers.register("INVITE", self.invited)
        self._handlers.register("PRIVMSG", self.privmsged)
        self._handlers.register("NOTICE", self.noticed)
        self._handlers.register("JOIN", self.joined)
        self._last = time.time()
        self._lastline = ""
        self._lock = _thread.allocate_lock()
        self._outqueue = queue.Queue()
        self._sock = None
        self._state.status = "running"
        self._userhosts = Object()
        self._threaded = False

    def _bind(self):
        """ find the internet adress of the IRC server (uses DNS). """
        server = self.cfg.server
        try:
            self._oldsock.bind((server, 0))
        except socket.error:
            if not server:
                try:
                    socket.inet_pton(socket.AF_INET6, self.cfg.server)
                except socket.error:
                    pass
                else:
                    server = self.cfg.server
            if not server:
                try:
                    socket.inet_pton(socket.AF_INET, self.cfg.server)
                except socket.error:
                    pass
                else:
                    server = self.cfg.server
            if not server:
                ips = []
                try:
                    for item in socket.getaddrinfo(self.cfg.server, None):
                        if item[0] in [socket.AF_INET, socket.AF_INET6] and item[1] == socket.SOCK_STREAM:
                            ip = item[4][0]
                            if ip not in ips:
                                ips.append(ip)
                except socket.error:
                    pass
                else: server = random.choice(ips)
        return server

    def _connect(self):
        """ create IRC socket, configure it and connect. """
        self._stopped = False
        if self.cfg.ipv6:
            self._oldsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self._oldsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = self._bind()
        self._error.status = ""
        self._cfg()

    def _cfg(self):
        """ configure the IRC socket. """
        self.blocking = True
        self._oldsock.setblocking(self.blocking)
        self._oldsock.settimeout(60.0)
        if not cfg.resume:
            logging.info("! connect %s:%s" % (self.cfg.server, self.cfg.port or 6667))
            self._oldsock.connect((self.cfg.server, int(str(self.cfg.port or 6667))))
        self._oldsock.setblocking(self.blocking)
        self._oldsock.settimeout(700.0)
        self.fsock = self._oldsock.makefile("r")
        if self.cfg.ssl:
            self._sock = ssl.wrap_socket(self._oldsock)
        else:
            self._sock = self._oldsock
        self._sock.setblocking(self.blocking)
        self._resume.fd = self._sock.fileno()
        if cfg.reboot:
            os.set_inheritable(self._sock, os.O_RDWR)
        self.register_fd(self._sock)

    def _some(self):
        """ read from socket, add to buffer and return last line. """
        try:
            if self.cfg.ssl:
                inbytes = self._sock.read()
            else:
                inbytes = self._sock.recv(512)
        except ConnectionResetError:
            raise EDISCONNECT(self.cfg.server)
        txt = str(inbytes, self.cfg.encoding)
        if txt == "":
            raise EDISCONNECT(self.cfg.server)
        self._lastline += txt
        splitted = self._lastline.split("\r\n")
        for s in splitted[:-1]:
            self._buffer.append(s)
            if not s.startswith("PING") and not s.startswith("PONG"):
                logging.debug(s.strip())
        self._lastline = splitted[-1]

    def announce(self, txt):
        """ announce txt to all joined channels. """
        for channel in self.channels:
            self._outqueue.put_nowait((channel, txt))

    def close(self):
        """ close the irc sockets, """
        if self.ssl:
            self.oldsock.shutdown(1)
            self.oldsock.close()
        else:
            self._sock.shutdown(1)
            self._sock.close()
        self.fsock.close()

    def connect(self):
        """ connect to server. """
        if cfg.resume:
            self.resume()
            return
        while 1:
            self._counter.connect += 1
            try:
                self._connect()
                self.logon()
                break
            except (EDISCONNECT,
                    BrokenPipeError,
                    ConnectionResetError) as ex:
                        logging.error("# disconnect #%s %s %s" % (self._counters.connect, self.server, str(ex)))
                        self._state.status = str(ex)
            logging.info("! sleeping %s seconds" % (self._counters.connect * 30))
            time.sleep(self._counters.connect * 30) 

    def dispatch(self, event):
        """ function called to dispatch event to it's handler. """
        for handler in self._handlers.get(event.command, []):
            handler(event)

    def event(self):
        """ return an event from the buffer (if available). """
        if not self._buffer:
            self._some()
        line = self._buffer.pop(0)
        e = self.parsing(line.rstrip())
        e.btype = self.type
        return e

    def join(self, channel, password=""):
        """ join a channel. """
        if password:
            self.raw('JOIN %s %s' % (channel, password))
        else:
            self.raw('JOIN %s' % channel)
        if channel not in self.channels:
            self.channels.append(channel)

    def joinall(self):
        """ join all channels. """
        if self.cfg.channel and self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        for channel in self.channels:
            self.join(channel)

    def logon(self, *args):
        """ logon to the IRC network. """
        self.raw("NICK %s" % self.cfg.nick or "botlib")
        self.raw("USER %s localhost %s :%s" % (self.cfg.username,
                                               self.cfg.server,
                                               self.cfg.realname))

    def out(self, channel, line):
        """ output method, split into 375 char lines, sleep 3 seconds. """
        for txt in split_txt(line, 375):
            self.privmsg(channel, str(txt))
            if time.time() - self._last < 3.0:
                time.sleep(3.0)

    def output(self):
        """ output loop reading from _outqueue. """
        while not self._stopped:
            args = self._outqueue.get()
            if self._stopped:
                break
            try:
                self.out(*args)
            except (EDISCONNECT, BrokenPipeError, ConnectionResetError) as ex:
                logging.error("# disconnect #%s %s %s" % (self._counter.push, self.cfg.server, str(ex)))
                self._error.status = str(ex)
                self._counter.push += 1
                time.sleep(10 + self._counter.push * 3.0)

    def parsing(self, txt):
        """ parse txt line into an Event. """
        rawstr = str(txt)
        obj = Event()
        obj.txt = ""
        obj.server = self.cfg.server
        obj.cc = self.cc
        obj.id = self.id()
        obj.arguments = []
        arguments = rawstr.split()
        obj.origin = arguments[0]
        if obj.origin.startswith(":"):
            obj.origin = obj.origin[1:]
            if len(arguments) > 1:
                obj.command = arguments[1]
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        obj.arguments.append(arg)
                    obj.txt = " ".join(txtlist)
        else:
            obj.command = obj.origin
            obj.origin = self.cfg.server
        try:
            obj.nick, obj.userhost = obj.origin.split("!")
        except:
            pass
        if obj.arguments:
            obj.target = obj.arguments[-1]
        else:
            obj.target = ""
        if obj.target.startswith("#"):
            obj.channel = obj.target
        if not obj.txt and len(arguments) == 1:
            obj.txt = arguments[1]
        if not obj.txt:
            obj.txt = rawstr.split(":")[-1]
        obj.id = self.id()
        return obj

    def part(self, channel):
        """ leave a channel. """
        self.raw('PART %s' % channel)
        if channel in self.channels:
            self.channels.remove(channel)
            self.save()

    def raw(self, txt):
        """ send txt over the socket to the server. """
        if "PING" not in txt and "PONG" not in txt:
            logging.debug(txt)
        if self._error.status:
            return
        if self._status == "error":
            return
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt = bytes(txt, "utf-8")
        self._last = time.time()
        try:
            self._sock.send(txt)
            return
        except (BrokenPipeError, ConnectionResetError):
            pass
        except AttributeError:
            try:
                self._sock.write(txt)
                return
            except (BrokenPipeError, ConnectionResetError):
                return

    def resume(self):
        """ resume the bot after reboot, creating stateless reboot. """
        f = Fleet().load(os.path.join(cfg.workdir, "runtime", "fleet"))
        for b in f:
            bot = compose(b)
            if bot and bot.id() == self.id():
                fd = bot._resume.fd
        if not fd:
            self.announce("resume failed")
            return
        self.channels = bot["channels"]
        logging.warn("# resume %s %s" % (fd, ",".join([str(x) for x in self.channels])))
        if self.cfg.ipv6:
            self._oldsock = socket.fromfd(fd, socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self._oldsock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        self._cfg()
        event = Event()
        party = Register().load(os.path.join(cfg.workdir, "runtime", "partyline"))
        for origin, fds in party.items():
            if origin.startswith("_"):
                continue
            event.origin = origin
            for fd in fds:
                s = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
                launcher.launch(self.dccloop, event, s)
        self.announce("done")

    def say(self, channel, txt):
        """ say txt on a channel. """
        self._outqueue.put_nowait((channel, txt))

    def start(self, *args, **kwargs):
        """ start the IRC bot. """
        super().start(*args, **kwargs)
        self.connect()
        launcher.launch(self.output)

    def stop(self):
        """ stop the IRC bot. """
        self._outqueue.put(None)
        super().stop()
        self.quit("http://bitbucket.org/bthate/botlib")
 
    def noticed(self, event):
        """ called when the bot is being noticed. """
        pass

    def connected(self, event):
        """ called when the bot is connected. """
        if "servermodes" in self.cfg:
            self.raw("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
        logging.info("! connected %s:%s" % (self.cfg.server, self.cfg.port))
        self.joinall()
        self._error.status = ""

    def invited(self, event):
        """ called when the bot is invited to a channel. """
        self.join(event.channel)

    def joined(self, event):
        """ called when someone joined a channel. """
        self.who(event.channel)
        if event.channel not in self.channels:
            self.channels.append(event.channel)

    def errored(self, event):
        """ error handler. """
        self._error.status = event.txt
        logging.error(event.txt)
        self.stop()

    def pinged(self, event):
        """ ping callback. """
        self.pongcheck = True
        self.pong(event.txt)
        self.ready()

    def ponged(self, event):
        """ pong callback. """
        self.pongcheck = False

    def quited(self, event):
        """ called when someone quits IRC. """
        if ("Ping timeout" in event.txt or "Excess Flood" in event.txt) and event.nick == self.cfg.nick:
            self.connect()

    def privmsged(self, event):
        """ PRIVMSG callback, forwards the event to the kernel for handling. """
        if event.txt.startswith("\001DCC"):
            self.dccconnect(event)
            return
        elif event.txt.startswith("\001VERSION"):
            self.ctcpreply(event.nick, "VERSION BOTLIB #%s - http://pypi.python.org/pypi/botlib" % __version__)
            return
        kernel.put(event)

    def ctcped(self, event):
        """ called when the bot is CTCP'ed. """
        pass

    def h001(self, event):
        """ 001 handler. """
        pass

    def h002(self, event):
        """ 002 handler. """
        pass

    def h003(self, event):
        """ 003 handler. """
        pass

    def h004(self, event):
        """ 004 handler. """
        pass

    def h005(self, event):
        """ 005 handler. """
        pass

    def h352(self, event):
        """ 352 handler. """
        args = event.arguments
        self._userhosts[args[5]] = args[2] + "@" + args[3]

    def h353(self, event):
        """ 353 handler. """
        pass

    def h366(self, event):
        """ 366 handler. """
        pass

    def h433(self, event):
        """ 433 handler. """
        self.donick(event.target + "_")

    def h513(self, event):
        """ 513 PING response handler. """
        self.raw("PONG %s" % event.txt.split()[-1])

    def donick(self, nick):
        """ change nick of the bot. """
        self.raw('NICK %s\n' % nick[:16])
        self.cfg.nick = nick
        self.sync()

    def who(self, channel):
        """ send a WHO query. """
        self.raw('WHO %s' % channel)

    def names(self, channel):
        """ send a NAMES query. """
        self.raw('NAMES %s' % channel)

    def whois(self, nick):
        """ send a WHOIS query. """
        self.raw('WHOIS %s' % nick)

    def privmsg(self, channel, txt):
        """ send a PRIVMSG. """
        self.raw('PRIVMSG %s :%s' % (channel, txt))

    def voice(self, channel, nick):
        """ send a MODE +v. """
        self.raw('MODE %s +v %s' % (channel, nick))

    def doop(self, channel, nick):
        """ send a MODE +o. """
        self.raw('MODE %s +o %s' % (channel, nick))

    def delop(self, channel, nick):
        """ send a MODE -o. """
        self.raw('MODE %s -o %s' % (channel, nick))

    def quit(self, reason='https://pikacode.com/bart/mad'):
        """ send a QUIT message with a reason for quitting. """
        self.raw('QUIT :%s' % reason)

    def notice(self, channel, txt):
        """ send NOTICE to channel/nick. """
        self.raw('NOTICE %s :%s' % (channel, txt))

    def ctcp(self, nick, txt):
        """ send CTCP to nick. """
        self.raw("PRIVMSG %s :\001%s\001" % (nick, txt))

    def ctcpreply(self, channel, txt):
        """ send a NOTICE message in reply to a CTCP message. """
        self.raw("NOTICE %s :\001%s\001" % (channel, txt))

    def action(self, channel, txt):
        """ send a /me ACTION. """
        self.raw("PRIVMSG %s :\001ACTION %s\001" % (channel, txt))

    def getchannelmode(self, channel):
        """ query channel modes. """
        self.raw('MODE %s' % channel)

    def settopic(self, channel, txt):
        """ set topic on a channel. """
        self.raw('TOPIC %s :%s' % (channel, txt))

    def ping(self, txt):
        """ send PING. """
        self.raw('PING :%s' % txt)

    def pong(self, txt):
        """ send PONG. """
        self.raw('PONG :%s' % txt)

    def dcced(self, event, s):
        """ DCC callback. Starts a DCC thread. """
        s.send(bytes('Welcome to BOTLIB ' + event.nick + " !!\n", self.cfg.encoding))
        launcher.launch(self.dccloop, event, s)

    def dccloop(self, event, s):
        """ loop on a DCC socket reading commands from it. """
        sockfile = s.makefile('rw')
        s.setblocking(True)
        if cfg.reboot:
            os.set_inheritable(s.fileno(), os.O_RDWR)
        partyline.register(event.origin, s.fileno())
        while 1:
            try:
                res = sockfile.readline()
                if not res:
                    break
                res = res.rstrip()
                logging.debug("DCC %s %s" % (event.origin, res))
                e = Event()
                e._socket = sockfile
                e.cc = ""
                e.btype = "irc"
                e.server = event.server
                e.txt = res
                e.origin = event.origin
                e.parse()
                kernel.put(e)
            except socket.timeout:
                time.sleep(0.01)
            except socket.error as ex:
                if ex.errno in [socket.EAGAIN, ]:
                    continue
                else:
                    raise
        sockfile.close()
        del partyline[event.origin]

    def dccconnect(self, event):
        """ connect to a DCC socket. """
        event.parse()
        addr = event._parsed.args[2]
        port = event._parsed.args[3][:-1]
        port = int(port)
        if re.search(':', addr):
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((addr, port))
        self.dcced(event, s)
