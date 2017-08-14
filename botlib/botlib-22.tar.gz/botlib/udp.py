# BOTLIB Framework to program bots
#
# botlib/udp.py
#
# Copyright 2017 B.H.J Thate
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" relay txt through a udp port listener. """

from .object import Object

import logging
import socket
import time

def init(*args, **kwargs):
    udp = UDP()
    udp.start()
    return udp

def shutdown(event):
    from .space import runtime
    udps = runtime.get("UDP", [])
    for udp in udps:
        udp.exit()

class UDP(Object):

    """ UDP class to echo txt through the bot, use the mad-udp program to send. """

    def __init__(self):
        super().__init__(self)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.setblocking(1)
        self._starttime = time.time()

    def start(self, *args, **kwargs):
        """ start the UDP server. """
        from .space import launcher
        launcher.launch(self.server)

    def server(self, host="", port="", *args, **kwargs):
        from .space import runtime
        logging.info("! start %s:%s" % (host or self.cfg.host, port or self.cfg.port))
        runtime.register("UDP", self)
        self._sock.bind((host or self.cfg.host, port or self.cfg.port))
        self._state.status = "run"
        while self._status:
            (txt, addr) = self._sock.recvfrom(64000)
            if not self._status:
                break
            data = str(txt.rstrip(), "utf-8")
            if not data:
                break
            self.output(data, addr)
        self.ready()
        logging.info("! stop udp %s:%s" % (self.cfg.host, self.cfg.port))

    def exit(self):
        """ shutdown the UDP server. """
        self._state.status = "stop"
        self._sock.settimeout(0.01)
        self._sock.sendto(bytes("bla", "utf-8"), (self.cfg.host, self.cfg.port))

    def output(self, txt, addr=None):
        """ output to all bot on fleet. """
        from .space import fleet, partyline
        try:
            (passwd, text) = txt.split(" ", 1)
        except:
            return
        text = text.replace("\00", "")
        if passwd == self.cfg.password:
            for orig, sockets in partyline.items():
                for sock in sockets:
                    sock.write(text)
                    sock.write("\n")
                    sock.flush()
