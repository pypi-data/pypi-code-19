"""
sentry_swift_nodestore.backend
~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2017 by Phillip Couto.
:license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import

import json
from time import sleep

import swiftclient

from sentry.nodestore.base import NodeStorage

class SwiftNodeStorage(NodeStorage):

    def __init__(self, container_name=None, auth_url=None, user=None, key=None):
        self.conn = swiftclient.Connection(auth_url, user, key, auth_version=1)
        self.container = container_name

    def delete(self, id):
        """
        >>> nodestore.delete('key1')
        """
        self.conn.delete_object(self.container, id)
    def get(self, id):
        """
        >>> data = nodestore.get('key1')
        >>> print data
        """
        hdrs, body = self.conn.get_object(self.container, id)
        return json.loads(body)
    def set(self, id, data):
        """
        >>> nodestore.set('key1', {'foo': 'bar'})
        """
        self.conn.put_object(self.container, id, json.dumps(data))