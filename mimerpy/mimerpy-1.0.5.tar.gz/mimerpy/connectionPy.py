# Copyright (c) 2017 Mimer Information Technology

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# See license for more details.

import connection
import weakref
from mimerpy.cursorPy import *
from mimerpy.mimPyExceptionHandler import *
import warnings
import sys

def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    """
    If cursor is not None, (errorclass, errorvalue) is appended to
    cursor.messages; otherwise it is appended to
    connection.messages. Then errorclass is raised with errorvalue as
    the value.
    You can override this with your own error handler by assigning it
    to the instance.
    """
    #sys.tracebacklimit = 1
    error = errorclass, errorvalue
    if cursor:
        cursor.messages.append(error)
    else:
        connection.messages.append(error)

    raise errorclass(errorvalue)


class Connection:

    """MimerSQL database connection"""

    def __init__(self, *args, **kwargs):
        """

            Creates a database connection. For more information please visit
            http://developer.mimer.com/python.

            dsn
                Data source name

            user
                Name of the ident to use

            password
                Password to chosen ident

        """
        dsn = kwargs.pop('dsn', None)
        user = kwargs.pop('user', None)
        password = kwargs.pop('password', None)
        self.autocommitmode = kwargs.pop('autocommit', False)
        self.errorhandler = kwargs.pop('errorhandler', defaulterrorhandler)
        self.messages = []
        self.__session = None
        self._rc_value = None
        self.__cursors = weakref.WeakSet()
        self._transaction = False
        L = connection.mimerBeginSessionC(dsn, user, password)
        self.__session = L[0]
        self._rc_value = L[1]
        self.__check_for_exception(self._rc_value, self.__session)


    def __enter__(self):
        return self

    def __exit__(self,type, value, traceback):
        self.__check_if_open()
        self.close()

    def __del__(self):
        if (not self.__session == None):
            self.close()

    def close(self):
        """Closes the database connection."""
        if(not self.__session == None):
            for x in self.__cursors: x.close()
            self._rc_value = connection.mimerEndTransaction(self.__session, 1)
            self.__check_for_exception(self._rc_value, self.__session)
            self._rc_value = connection.mimerEndSession(self.__session)
            self.__check_for_exception(self._rc_value, self.__session)
            self.__session = None
            self._transaction = False


    def rollback(self):
        """Rolls back any pending transaction."""
        self.__check_if_open()
        self._rc_value = connection.mimerEndTransaction(self.__session, 1)
        self.__check_for_exception(self._rc_value, self.__session)
        self._transaction = False

    def commit(self):
        """Commits any pending transaction."""
        self.__check_if_open()
        self._rc_value = connection.mimerEndTransaction(self.__session, 0)
        self.__check_for_exception(self._rc_value, self.__session)
        self._transaction = False

    def cursor(self, **kwargs):
        """Returns a new Cursor Object using the connection."""
        self.__check_if_open()
        kwargs2 = kwargs.copy()
        mode = kwargs2.pop('scrollable', False)
        if (mode):
             curs = ScrollCursor(self, self.__session)
        else:
             curs = Cursor(self, self.__session)

        self.__cursors.add(curs)
        return curs

    def execute(self, *arg):
        """
            Creates a cursor and executes a database operation.

            arg
                query to execute

            Returns a new Cursor object using the connection and executes
            a database operation.

        """
        self.__check_if_open()
        curs = Cursor(self, self.__session)
        self.__cursors.add(curs)
        curs.execute(*arg)
        return curs

    def executemany(self, *arg):
        """
            Creates a cursor and executes a database operation.

            arg
                query to execute and parameter sequences.

            Returns a new Cursor object using the connection and executes
            a database operation against all parameter sequences or mappings
            found in args.

        """
        self.__check_if_open()
        curs = Cursor(self, self.__session)
        self.__cursors.add(curs)
        curs.executemany(*arg)
        return curs

    def autocommit(self, mode):
        """
        Turns autocommit mode on or off. Defualt is false

        arg
            Boolean
        """
        if(mode):
            self.autocommitmode = True
            if (self._transaction):
                self.rollback()
        else:
            self.autocommitmode = False

    def __check_if_open(self):
        if(self.__session == None):
            self.__check_for_exception(-25000, "Connection not open")

    def __check_for_exception(self, *arg):
        m = check_for_exception(arg[0], arg[1])
        if(isinstance(m,tuple)):
            if(m[0]):
                self.errorhandler(self, None, m[0], (m[1]))

    def xid(self):
        raise NotSupportedError("TPC transaction IDs not supported");

    def tpc_begin(self):
        raise NotSupportedError("TPC transaction IDs not supported");

    def tpc_prepare(self):
        raise NotSupportedError("TPC transaction IDs not supported");

    def tpc_commit(self):
        raise NotSupportedError("TPC transaction IDs not supported");

    def tpc_rollback(self):
        raise NotSupportedError("TPC transaction IDs not supported");

    def tpc_recover(self):
        raise NotSupportedError("TPC transaction IDs not supported");
