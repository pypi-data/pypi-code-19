# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2016 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pytestsalt.utils.ipc
    ~~~~~~~~~~~~~~~~~~~~

    IPC Server/Client for communication between salt daemons and pytest-salt plugin
'''

import logging

import msgpack
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.tcpclient import TCPClient
from tornado.tcpserver import TCPServer
from tornado.netutil import add_accept_handler, bind_unix_socket

log = logging.getLogger(__name__)


class IPCServer:
    def __init__(self, socket_path, io_loop=None):
        self.socket_path = socket_path
        self._started = self._closing = False
        self.io_loop = io_loop or IOLoop.current()
        self._event_registry = {}

    def start(self):
        if self._started:
            return
        log.info('%s binding to: %s', self.__class__.__name__, self.socket_path)
        self._closing = False
        self.sock = bind_unix_socket(self.socket_path)
        add_accept_handler(self.sock,
                           self.handle_connection,
                           io_loop=self.io_loop)
        self._started = True

    def stop(self):
        if not self._started:
            return
        if self._closing:
            return
        log.info('%s stopping', self.__class__.__name__)
        self._closing = True
        if hasattr(self, 'sock'):
            self.sock.close()
        self._started = False

    def handle_connection(self, connection, address):
        log.info('%s handling connection to: %s', self.__class__.__name__, address)
        try:
            stream = IOStream(connection, io_loop=self.io_loop)
            self.io_loop.spawn_callback(self.handle_stream, stream)
        except Exception as exc:
            log.error('%s streaming error: %s', self.__class__.__name__, exc)
            log.exception(exc)

    @gen.coroutine
    def handle_stream(self, stream):
        unpacker = msgpack.Unpacker(encoding='utf-8')
        while not stream.closed():
            try:
                wire_bytes = yield stream.read_bytes(4096, partial=True)
                unpacker.feed(wire_bytes)
                for action, events in unpacker:
                    if action == 'subscribe':
                        for event in events:
                            self._event_registry.setdefault(event, set()).add(stream)
                    elif action == 'unsubscribe':
                        for event in events:
                            if event in self._event_registry:
                                if stream in self._event_registry[event]:
                                    self._event_registry[event].remove(stream)



class Client(TCPClient):
    pass
