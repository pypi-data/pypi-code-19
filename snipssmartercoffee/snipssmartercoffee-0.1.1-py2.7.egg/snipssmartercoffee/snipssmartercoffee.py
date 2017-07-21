#!/usr/bin/env python3
# encoding: utf-8

import socket


class SnipsSmarterCoffee:

    SMARTER_PORT = 2081
    BUFFER_SIZE = 10
    
    def __init__(self, hostname):
        self.hostname = hostname

    def brew(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.hostname, self.SMARTER_PORT))
            s.send("7")
            data = s.recv(self.BUFFER_SIZE)
            s.close()
        except socket.error, msg:
            return
