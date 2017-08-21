"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol.packet import *  #noqa

import json
import logging
import traceback

pplog = logging.getLogger('pubkeeper.protocol')


def require_auth(perm=None):
    def func_wrapper(func):
        def wrapper(self, *args, **kwargs):
            if self.server_authenticated:
                if perm is None \
                        or perm in self.permissions \
                        or 'all' in self.permissions:
                    func(self, *args, **kwargs)
                else:
                    self.write_message(ErrorPacket(
                        message='Lack Permissions for Request {0}'.format(perm)
                    ))
                    pplog.error("Lack Permissions for Request {0}".format(perm))
            else:
                self.write_message(ErrorPacket(
                    message='Unauthenticated Request'
                ))
                pplog.error("Unauthenticated request to {0}".format(func))

        return wrapper

    return func_wrapper


class PubkeeperProtocol():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers = {
            Packet.ERROR: self.on_error,
        }
        self.server_authenticated = False
        self.client_authenticated = False
        self.permissions = []

    def on_message(self, message):
        """Handle Incoming Message

        Will handle incoming messages from WebSocket and send to
        respective handler

        Args
            message (string) - Data received from WebSocket
        """
        try:
            frame = json.loads(message)
            pplog.debug("Received: {0} - {1}".
                        format(Packet(frame[0]).name, frame[1]))
            if Packet(frame[0]) in self.handlers:
                self.handlers[Packet(frame[0])](**frame[1])
            else:
                pplog.warning("There is no handler for: {0} - {1}".
                              format(Packet(frame[0]).name, frame[1]))
        except Exception as e:
            if Packet(frame[0]) is not Packet.ERROR:
                pplog.error('Action error ({0})'.format(e))
                traceback.print_tb(e.__traceback__)
                self.write_message(ErrorPacket(
                    message='Action error ({0})'.format(e)
                ))

    def on_error(self, message):
        """on_error

        Called when a ERROR packet is received

        Args:
            message (string) - Error String
        """
        pass
