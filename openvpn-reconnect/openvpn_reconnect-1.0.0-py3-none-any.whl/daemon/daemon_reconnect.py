# encoding:utf-8

from time import sleep

from openvpn_reconnect.daemon.daemon import Daemon
from openvpn_reconnect.program.reconnect import ping, restart_openvpn
from openvpn_reconnect.program.statics import Statics


class DaemonReconnect(Daemon):
    def run(self):
        while True:
            if ping(host=Statics.HOST, interface=Statics.INTERFACE, packets=Statics.PACKETS) != 0:
                restart_openvpn()
            sleep(Statics.SECONDS)
