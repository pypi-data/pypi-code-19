import os
import unittest2

import pymysql


class PyMySQLProxyCursorTestCase(unittest2.TestCase):

    def setUp(self):
        host = os.environ.get('DB_HOST', 'localhost')
        user = os.environ.get('DB_USER', 'root')
        passwd = os.environ.get('DB_PASSWD', '')
        db = os.environ.get('DB_DB', 'test_db')

        databases = [{
            "host": host,
            "user": user,
            "passwd": passwd,
            "db": db,
            "use_unicode": True,
            "autocommit": False
        }]

        self.connections = []
        for params in databases:
            self.connections.append(pymysql.connect(**params))
            self.addCleanup(self._teardown_connections)

    def _teardown_connections(self):
        for connection in self.connections:
            connection.close()
