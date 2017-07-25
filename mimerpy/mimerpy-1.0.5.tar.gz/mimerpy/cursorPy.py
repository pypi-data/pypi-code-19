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

from mimerpy.mimPyExceptionHandler import *
import cursor
import connection
import collections

get_funcs = {1:cursor.mimerGetStringC,6:cursor.mimerGetInt32,10:cursor.mimerGetDouble,
11:cursor.mimerGetStringC, 34:cursor.mimerGetBinary,40:cursor.mimerGetStringC,
42:cursor.mimerGetBoolean, 48:cursor.mimerGetInt32,50:cursor.mimerGetInt32,52:cursor.mimerGetInt64,63:cursor.mimerGetStringC,
56:cursor.mimerGetDouble, 54:cursor.mimerGetDouble, 57:cursor.mimerGetBlobData,
58:cursor.mimerGetNclobDataC,59:cursor.mimerGetNclobDataC}
set_funcs = {1:cursor.mimerSetStringC,6:cursor.mimerSetInt32,10:cursor.mimerSetDouble,
11:cursor.mimerSetStringC, 34:cursor.mimerSetBinary,
40:cursor.mimerSetStringC, 42:cursor.mimerSetBoolean, 48:cursor.mimerSetInt32,
50:cursor.mimerSetInt32,52:cursor.mimerSetInt64,63:cursor.mimerSetStringC,56:cursor.mimerSetDouble, 54:cursor.mimerSetDouble,
57:cursor.mimerSetBlobData, 58:cursor.mimerSetNclobDataC,59:cursor.mimerSetNclobDataC, 501:cursor.mimerSetNull}


class Cursor:

    """MimerSQL Cursor."""

    def __init__(self, connection, session, **kwargs):
        """

            Creates a cursor . For more information please visit
            http://developer.mimer.com/python.

            session
                reference to MimerSession sessionhandle.

        """
        kwargs2 = kwargs.copy()
        self.connection = connection
        self.__session = session
        self.rowcount = -1
        self._rc_value = None
        self.__statement = None
        self._number_of_parameters = None
        self._number_of_columns = None
        self.arraysize = 1
        self._last_query = None
        self._DDL_rc_value = None
        self.__mimcursor = False
        self.errorhandler = connection.errorhandler
        self.messages = []
        self.description = None

    def __enter__(self):
        self.__check_if_open()
        return self

    def __exit__(self,type, value, traceback):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        self.__check_if_open()
        return_value = self.fetchone()
        if return_value == []:
            raise StopIteration
        return return_value

    def __del__(self):
        self.close()

    def close(self):
        """Closes the cursor. """
        self.__close_statement()
        self.__session = None

    def execute(self, *arg):
        """
            Executes a database operation.

            arg
                query to execute

            Executes a database operation.

        """
        self.__check_if_open()
        self.__check_for_transaction()
        query = ()
        values = []
        self._rc_value = 0
        #teporay fix for single paramarker
        if(len(arg) > 1):
            if(not isinstance(arg[1], tuple) and (not isinstance(arg[1], list))):
                pMarkers = [arg[1]]
            else:
                pMarkers = arg[1]
        query = arg[0]

        if(query != self._last_query or self.__mimcursor):
            self.__close_statement()
            values = cursor.mimerBeginStatementC(self.__session, query, 0)
            self._rc_value = values[0]
            self._DDL_rc_value = values[0]
            if(self._DDL_rc_value != -24005):
                self.__check_for_exception(self._rc_value, self.__session)
                self.__statement = values[1]

        self._last_query = query

        #Return value -24005 is given when a DDL query query is passed through
        #mimerBeginStatementC.g
        if(self._DDL_rc_value == -24005):
            self.connection.transaction = False
            self.messages = []
            self._rc_value = cursor.mimerExecuteStatementC(self.__session, query)
            self.__check_for_exception(self._rc_value, self.__session)
        else:
            self._rc_value = cursor.mimerParameterCount(self.__statement)
            self.__check_for_exception(self._rc_value, self.__statement)

            #Return value of mimerParameterCount = 0 implies a query with no
            #parameters.
            if(self._rc_value > 0):
                self._number_of_parameters = self._rc_value
                try:
                    if(len(pMarkers)!=self._number_of_parameters):
                        # inte helt korrekt

                        self.__check_for_exception(-25103, "Invalid number of parameters")
                    for a in range(1, self._number_of_parameters + 1):
                        self._rc_value = cursor.mimerParameterType(self.__statement, a)
                        self.__check_for_exception(self._rc_value, self.__statement)
                        if(pMarkers[a - 1] == None):
                            self._rc_value = 501
                        self._rc_value = set_funcs[self._rc_value](self.__statement, a,
                                                              pMarkers[a - 1])
                        self.__check_for_exception(self._rc_value, self.__statement)

                except TypeError as e:
                    self.__check_for_exception(-25107, e)
                except OverflowError as e:
                    self.__check_for_exception(-25107, e)

            self.__check_for_exception(self._rc_value, self.__statement)
            self._rc_value = cursor.mimerColumnCount(self.__statement)
            #Return value of mimerColumnCount <= 0 implies a query with no
            #result set.
            if (self._rc_value <= 0):
                self.__check_for_exception(self._rc_value, self.__statement)
                self.messages = []
                self._rc_value = cursor.mimerExecute(self.__statement)
                self.__check_for_exception(self._rc_value, self.__statement)
                self.rowcount = self._rc_value
            else:
                #Return value of mimerColumnCount > 0 implies a query with a
                #result set.
                self._number_of_columns = self._rc_value
                self._rc_value = cursor.mimerOpenCursor(self.__statement)
                self.__check_for_exception(self._rc_value, self.__statement)
                self.__mimcursor = True
                description = collections.namedtuple('Column_description',
                'name type_code display_size internal_size precision scale null_ok')
                self.description = ()
                for a in range(1, self._number_of_columns + 1):
                    func_tuple = cursor.mimerColumnNameC(self.__statement, a)
                    self._rc_value = func_tuple[0]
                    self.__check_for_exception(self._rc_value, self.__statement)
                    name = func_tuple[1]
                    self._rc_value = cursor.mimerColumnType(self.__statement, a)
                    self.__check_for_exception(self._rc_value, self.__statement)
                    type_code = self._rc_value
                    self.description = self.description + (description(name=name,
                                                            type_code=type_code,
                                                            display_size=None,
                                                            internal_size=None,
                                                            precision=None,
                                                            scale=None,
                                                            null_ok=None),)

    def executemany(self, query, params):
        """
            Executes a database operation.

            query
                query with parameter markers to execute.

            params
                sequence of parameters.

            Executes a database operation against all parameter sequences or mappings
            found in params.

        """
        self.__check_if_open()
        self.__check_for_transaction()
        values = []
        self._rc_value = 0
        self._last_query = None

        if(not isinstance(params, tuple) and not isinstance(params, list)):
            self.__check_for_exception(-26001, "Invalid parameter format")

        else:
            if(not isinstance(params[0], tuple)):
                self.__check_for_exception(-26001, "Invalid parameter format")

        self.__close_statement()
        values = cursor.mimerBeginStatementC(self.__session, query, 0)
        self._rc_value = values[0]

        self.__check_for_exception(self._rc_value, self.__session)
        self.__statement = values[1]
        self.__check_for_exception(self._rc_value, self.__statement)

        self._rc_value = cursor.mimerParameterCount(self.__statement)
        self._number_of_parameters = self._rc_value

        self.rowcount = 0
        self.__check_for_exception(self._rc_value, self.__statement)
        try:
            for laps in range(0, len(params)):
                cur_v = params[laps]
                for a in range(1, self._number_of_parameters + 1):
                    self._rc_value = cursor.mimerParameterType(self.__statement, a)
                    self.__check_for_exception(self._rc_value, self.__statement)
                    if(cur_v[a - 1] == None):
                        self._rc_value = 501
                    self._rc_value = set_funcs[self._rc_value](self.__statement, a, cur_v[a - 1])
                self.messages = []
                self._rc_value = cursor.mimerExecute(self.__statement)
                self.__check_for_exception(self._rc_value, self.__statement)
                self.rowcount = self.rowcount + self._rc_value
        except TypeError as e:
            self.__check_for_exception(-25107, e)
        except OverflowError as e:
            self.__check_for_exception(-25107, e)


    def fetchone(self):
        """Fetch next row of a query result set."""
        self.__check_if_open()
        self.__check_for_transaction()
        if(not self.__mimcursor):
            self.__check_for_exception(-25107, "Previous execute did not produce any result set")
        self._rc_value = cursor.mimerFetch(self.__statement)
        self.__check_for_exception(self._rc_value, self.__statement)
        return_tuple = ()

        #Return value of mimerFetch == 100 implies end of result set
        if(self._rc_value == 100):
            return []

        for a in range(1, self._number_of_columns + 1):
            self._rc_value = cursor.mimerColumnType(self.__statement, a)
            self.__check_for_exception(self._rc_value, self.__statement)
            func_tuple = get_funcs[self._rc_value](self.__statement, a)
            self.__check_for_exception(func_tuple[0], self.__statement)
            #Conversion from C int to python boolean
            if(self._rc_value==42):
                if(func_tuple[-1]==0):
                    return_tuple = return_tuple + (False,)
                else:
                    return_tuple = return_tuple + (True,)
            else:
                return_tuple = return_tuple + (func_tuple[1],)

        return return_tuple

    def fetchmany(self, *arg):
        """Fetch next row of a query result set.

        arg
            sets the arraysize

        The number of rows to fetch per call is specified by the parameter.
        If it is not given, the cursor's arraysize determines the number of
        rows to be fetched. The method should try to fetch as many rows as
        indicated by the size parameter. If this is not possible due to the
        specified number of rows not being available, fewer rows may be returned.

        Note: Arraysize is retained after each call to fetchmany.

        """
        self.__check_if_open()
        self.__check_for_transaction()
        if(not self.__mimcursor):
            self.__check_for_exception(-25107, "Previous execute did not produce any result set")
        values = []
        return_tuple = ()
        if(len(arg) > 0):
            self.arraysize = arg[0]

        fetch_length = self.arraysize
        self._rc_value = cursor.mimerFetch(self.__statement)
        fetch_value = self._rc_value
        while(fetch_value != 100 and fetch_length > 0):
            return_tuple = ()
            for a in range(1, self._number_of_columns + 1):
                self._rc_value = cursor.mimerColumnType(self.__statement, a)
                self.__check_for_exception(self._rc_value, self.__statement)
                func_tuple = get_funcs[self._rc_value](self.__statement, a)
                self.__check_for_exception(func_tuple[0], self.__statement)
                #Conversion from C int to python boolean
                if(self._rc_value==42):
                    if(func_tuple[-1]==0):
                        return_tuple = return_tuple + (False,)
                    else:
                        return_tuple = return_tuple + (True,)
                else:
                    return_tuple = return_tuple + (func_tuple[1],)

            values.append(return_tuple)
            fetch_length = fetch_length - 1
            fetch_value = cursor.mimerFetch(self.__statement)
        return values

    def fetchall(self):
        """Fetch all (remaining) row of a query result set."""
        self.__check_if_open()
        self.__check_for_transaction()
        if(not self.__mimcursor):
            self.__check_for_exception(-25107, "Previous execute did not produce any result set")
        values = []
        self._rc_value = cursor.mimerFetch(self.__statement)
        fetch_value = self._rc_value
        while(fetch_value != 100):
            return_tuple = ()
            for a in range(1, self._number_of_columns + 1):
                self._rc_value = cursor.mimerColumnType(self.__statement, a)
                self.__check_for_exception(self._rc_value, self.__statement)
                func_tuple = get_funcs[self._rc_value](self.__statement, a)
                self.__check_for_exception(func_tuple[0], self.__statement)
                #Conversion from C int to python boolean
                if(self._rc_value==42):
                    if(func_tuple[-1]==0):
                        return_tuple = return_tuple + (False,)
                    else:
                        return_tuple = return_tuple + (True,)
                else:
                    return_tuple = return_tuple + (func_tuple[1],)

            values.append(return_tuple)
            fetch_value = cursor.mimerFetch(self.__statement)
        return values

    def setinputsizes(self):
        """Does nothing but required by the DB API."""

    def setoutputsizes(self):
        """Does nothing but required by the DB API."""

    def next(self):
        """Advances to the next row of a query result set."""
        return_tuple = self.fetchone()
        if(return_tuple):
            return return_tuple
        else:
            raise StopIteration

    def __close_statement(self):
        #Private method for closing MimerStatement.
        if(self.__statement != None):
            self._rc_value = cursor.mimerEndStatement(self.__statement)
            self.__statement = None
            self.__mimcursor = False
            self.__check_for_exception(self._rc_value, self.__statement)

    def __check_if_open(self):
        if(self.__session == None):
            self.__check_for_exception(-25000, "Cursor not open")

    def __check_for_transaction(self):
        if(not self.connection._transaction and not self.connection.autocommitmode):
            self._rc_value = connection.mimerBeginTransaction(self.__session)
            self.__check_for_exception(self._rc_value, self.__session)
            self.connection._transaction = True

    def __check_for_exception(self, *arg):
        m = check_for_exception(arg[0], arg[1])
        if(isinstance(m,tuple)):
            if(m[0]):
                self.errorhandler(None, self, m[0], (m[1]))

    def nextset(self):
        raise(NotSupportedError("Not suppported"))

    def callproc(self):
        raise(NotSupportedError("Not suppported"))

class ScrollCursor(Cursor):

    def __init__(self, connection, session):
        super(ScrollCursor, self).__init__(connection, session)
        self.__result_set = None
        self.rownumber = None

    def execute(self, *arg):
        """
            Executes a database operation.

            arg
                query to execute

            Executes a database operation.

        """
        super(ScrollCursor, self).execute(*arg)
        if(self._Cursor__mimcursor):
            self.__result_set = super(ScrollCursor, self).fetchall()
            self.rowcount = len(self.__result_set)
            self.rownumber = 0
        else:
            self.__result_set = None

    def fetchone(self):
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()
        if(self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        values = ()
        try:
            values = values + self.__result_set[self.rownumber]
            self.rownumber = self.rownumber + 1
        except IndexError:
            return []
        return values


    def fetchmany(self, *arg):
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()
        if(self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        if(len(arg) > 0):
            self.arraysize = arg[0]

        fetch_size = self.arraysize
        values = []
        while(fetch_size):
            try:
                values.append(self.__result_set[self.rownumber])
                fetch_size = fetch_size - 1
                self.rownumber = self.rownumber + 1
            except IndexError:
                break
        return values

    def fetchall(self):
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()
        values = []
        if(self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        if (not self.rownumber):
            self.rownumber = len(self.__result_set)
            return self.__result_set
        else:
            values = self.__result_set[self.rownumber:len(self.__result_set)]
            self.rownumber = len(self.__result_set)
            return values

    def next(self):
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()
        if(self.__result_set == None):
            self._Cursor__check_for_exception(-25000, "Last execute did not produce a result set")
        if(self.__result_set == []):
            return self.__result_set
        values = ()
        try:
            values = values + self.__result_set[self.rownumber]
            self.rownumber = self.rownumber + 1
        except IndexError:
            raise StopIteration
        return values

    def scroll(self, value, mode = 'relative'):
        self._Cursor__check_if_open()
        self._Cursor__check_for_transaction()
        if(mode == 'relative'):
            new_row = self.rownumber + value
            if(new_row >= len(self.__result_set)):
                raise IndexError
            else:
                self.rownumber = new_row
        elif(mode == 'absolute'):
            if(value >= len(self.__result_set)):
                raise IndexError
            else:
                self.rownumber = value
        else:
            self._Cursor__check_for_exception(-25000, "Not a possible scroll mode")
