# NFQ Logwrapper. A tool for centralizing and visualizing logs.
# Copyright (C) 2017 Guillem Borrell Nogueras
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import logging

from collections import namedtuple
from tornado import websocket
from nfq.conductor.db import clients


ClientInfo = namedtuple('ClientInfo', ('client', 'subscription'))


class WSHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        clients.append(ClientInfo(self, None))
        logging.info("WebSocket opened")
        logging.info("{} clients registered".format(len(clients)))

    def on_message(self, message):
        this_client = None
        for i, c in enumerate(clients):
            if self is c.client:
                this_client = clients.pop(i)

        if this_client:
            if this_client.subscription is None:
                if message.startswith('SUB'):
                    clients.append(ClientInfo(self,
                                              re.compile(
                                                  message.replace('SUB', '')
                                              )
                                              )
                                   )
                    subscription = message.replace('SUB', '')
                    self.write_message("INFO: Client subscribed to {}".format(
                        subscription)
                    )

                    logging.info("Client subscribed to {}".format(
                        subscription)
                    )
                else:
                    self.write_message(
                        "ERROR: Initial message format not correct"
                    )
        else:
            logging.error('Client not found. This is a strange exception.')

    def on_close(self):
        this_client = None
        for i, c in enumerate(clients):
            if self is c.client:
                this_client = clients.pop(i)

        if this_client is not None:
            logging.info("WebSocket closed")
            logging.info("{} clients registered".format(len(clients)))

        else:
            logging.error("Client not found")
