# coding: utf8

from gevent.server import DatagramServer

from .mixins import AppEventsMixin
from .connection import Connection


class Server(AppEventsMixin):

    server_class = DatagramServer
    connection_class = Connection

    box_class = None

    # 连接最长不活跃时间
    timeout = None

    conv = None

    server = None
    conn_dict = None

    def __init__(self, box_class):
        super(Server, self).__init__()
        self.box_class = box_class
        self.conn_dict = dict()

    def handle(self, message, address):
        conn = self.conn_dict.get(address)
        if not conn:
            conn = self.connection_class(self, address)
            self.conn_dict[address] = conn

        conn.handle(message)

    def run(self, host, port, conv=None):
        class UDPServer(self.server_class):
            def handle(sub_self, message, address):
                return self.handle(message, address)

        self.conv = conv or 0
        self.server = UDPServer((host, port))
        self.server.serve_forever()

    @property
    def socket(self):
        return self.server.socket

    def remove_conn(self, conn):
        self.conn_dict.pop(conn.address, None)

    def has_conn(self, conn):
        return conn.address in self.conn_dict
