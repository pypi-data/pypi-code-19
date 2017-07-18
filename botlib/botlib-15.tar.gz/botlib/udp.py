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
        self._status = "start"
        self._starttime = time.time()

    def start(self, *args, **kwargs):
        """ start the UDP server. """
        from .space import launcher
        launcher.launch(self.server)

    def server(self, host="", port="", *args, **kwargs):
        from .space import runtime
        logging.info("! start udp %s:%s" % (host or self.cfg.host, port or self.cfg.port))
        runtime.register("UDP", self)
        self._sock.bind((host or self.cfg.host, port or self.cfg.port))
        self._status = "running"
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
        self._status = ""
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
