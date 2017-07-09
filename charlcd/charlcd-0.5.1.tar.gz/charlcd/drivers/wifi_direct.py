#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,W0231
"""Driver for WiFi direct"""

import socket
import json
import time
from charlcd.drivers.base import BaseDriver


class WiFi(BaseDriver):
    """WiFi direct driver"""
    def __init__(self, message, node_names, address):
        """
        :param message: Message class
        :param node_names: list with target nodes with lcds
        :param address: tuple broadcast IP and port
        """
        self.message = message
        self.address = address
        self.buffer = None
        self.socket = None
        if isinstance(node_names, list):
            self.node_names = node_names
        else:
            self.node_names = [node_names]

        self.pins = {'E2': 1}

    def init(self):
        """Initialize sockets"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def cmd(self, char, enable=0):
        """Prepare cmd event message"""
        message = self.message.prepare_message({
            'event': 'lcd.cmd',
            'parameters': {
                'data': char,
                'enable': enable
            },
            'targets': self.node_names
        })
        self.buffer = message
        self.send()

    def shutdown(self):
        pass

    def send(self, enable=0):
        """Convert dict into json string and broadcast packet"""
        try:
            msg = json.dumps(self.buffer)
            self.socket.sendto(
                msg.encode(),
                self.address
            )
            time.sleep(0.05)
        except ValueError:
            pass

    def write(self, char, enable=0):
        """Prepare write event message"""
        message = self.message.prepare_message({
            'event': 'lcd.write',
            'parameters': {
                'data': char,
                'enable': enable
            },
            'targets': self.node_names
        })
        self.buffer = message
        self.send()

    def char(self, char, enable=0):
        """Prepare char event message"""
        message = self.message.prepare_message({
            'event': 'lcd.char',
            'parameters': {
                'data': char,
                'enable': enable
            },
            'targets': self.node_names
        })
        self.buffer = message
        self.send()

    def set_mode(self, mode):
        pass
