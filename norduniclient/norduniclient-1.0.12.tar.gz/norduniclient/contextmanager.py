# -*- coding: utf-8 -*-

from __future__ import absolute_import

from contextlib import contextmanager
from norduniclient.core import get_db_driver

__author__ = 'lundberg'


class Neo4jDBSessionManager:

    """
    Every new connection is a transaction. To minimize new connection overhead for many reads we try to reuse a single
    connection. If this seem like a bad idea some kind of connection pool might work better.

    Neo4jDBSessionManager.read()
    When using with Neo4jDBSessionManager.read(): we will always rollback the transaction. All exceptions will be
    thrown.

    Neo4jDBSessionManager.write()
    When using with Neo4jDBSessionManager.write() we will always commit the transaction except when we see an
    exception. If we get an exception we will rollback the transaction and throw the exception.

    Neo4jDBSessionManager.transaction()
    When we don't want to share a connection (transaction context) we can set up a new connection which will work
    just as the write context manager above but with it's own connection.
    """

    def __init__(self, uri, username=None, password=None, encrypted=True):
        self.uri = uri
        self.driver = get_db_driver(uri, username, password, encrypted)

    @contextmanager
    def _session(self):
        session = self.driver.session()
        try:
            yield session
        except Exception as e:
            raise e
        finally:
            session.close()
    session = property(_session)

    @contextmanager
    def _transaction(self):
        session = self.driver.session()
        transaction = session.begin_transaction()
        try:
            yield transaction
        except Exception as e:
            transaction.success = False
            raise e
        else:
            transaction.success = True
        finally:
            session.close()
    transaction = property(_transaction)
