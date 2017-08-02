# -*- coding: utf-8 -*-
# <carbontube - distributed pipeline framework>
#
# Copyright (C) <2016>  Gabriel Falcão <gabriel@nacaolivre.org>
# (C) Author: Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import uuid
import logging

import zmq.green as zmq

from agentzero import SocketManager


class PipelineClient(object):
    """Pipeline client

    Has the ability to push jobs to a pipeline server
    """
    def __init__(self, address, hwm=10):
        """
        :param address: the zmq address in which to connect to
        """
        self.context = zmq.Context()
        self.sockets = SocketManager(zmq, self.context, polling_timeout=1, timeout=0.0001)
        self.sockets.create('jobs', zmq.PUSH)
        self.sockets.set_socket_option('jobs', zmq.SNDHWM, hwm)
        self.logger = logging.getLogger(__name__)
        self.address = address

    def connect(self):
        """
        connects to the server
        """
        return self.sockets.connect('jobs', self.address, zmq.POLLOUT)

    def enqueue_job(self, data):
        """pushes a job to the pipeline.

        **Note** that the data must be a dictionary with the following
          keys:

        * ``name`` - the pipeline name
        * ``instructions`` - a dictionary with instructions for the first phase to execute

        :param data: the dictionary with the formatted payload.
        :returns: the payload sent to the server, which contains the job id

        **EXAMPLE:**

        ::

            >>> from carbontube.clients import PipelineClient

            >>> properly_formatted = {
            ...     "name": "example1",
            ...     "instructions": {
            ...          "size": 100",
            ...     },
            ... }
            >>> client = PipelineClient('tcp://127.0.0.1:5050')
            >>> client.connect()
            >>> ok, payload_sent = client.enqueue_job(properly_formatted)
        """
        payload = {
            'id': uuid.uuid4().hex,
            'pipeline': True,
            'instructions': data,
        }

        return self.sockets.send_safe('jobs', payload), payload
