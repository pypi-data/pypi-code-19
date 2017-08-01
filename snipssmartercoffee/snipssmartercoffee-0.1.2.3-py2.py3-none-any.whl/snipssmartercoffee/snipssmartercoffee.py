# -*-: coding utf-8 -*-
""" Smarter Coffee skill for Snips. """

import socket


class SnipsSmarterCoffee:
    """ Smarter Coffee skill for Snips. """

    SMARTER_PORT = 2081
    BUFFER_SIZE = 10
    
    def __init__(self, hostname):
        """ Intialisation.

        :param hostname: The hostname of the Smarter Coffee machine.
        """
        self.hostname = hostname

    def brew(self):
        """ Start brewing. """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.hostname, self.SMARTER_PORT))
            s.send("7")
            data = s.recv(self.BUFFER_SIZE)
            s.close()
        except socket.error as msg:
            return
