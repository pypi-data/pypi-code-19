# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2017 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        databases.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     26/07/2017
# -------------------------------------------------------------------------------

from gecosistema_lite.filesystem import *
import time
import xlwt
import csv
import sqlite3 as sqlite

class AbstractDB:


    def __init__(self, filename):
        """
        Constructor
        """
        self.dsn = filename
        mkdirs(justpath(filename))
        self.conn = None
        self.__connect__()


    def __del__(self):
        self.close()


    def __get_cursor__(self):
        return self.conn.cursor()


    def __connect__(self):
        raise Exception("Not implemented here!")

    def GetTables(self):
        raise Exception("Not implemented here!")

    def GetFieldNames(self, tablename, ctype=""):
        raise Exception("Not implemented here!")

    def GetPrimaryKeys(self, tablename):
        raise Exception("Not implemented here!")

    def GetTablenameFromQuery(sql):
        expr = '(?<=from|join)\s+{tablelist}\s*(,|;)?'
        tablename = '(?P<tablename>(\[(.*?)\])|(\w+))'
        tablelist = '(?P<database>(\[(.*?)\])|(\w+))(\.(?P<tablename>(\[(.*?)\])|(\w+)))?'
        expr = sformat(expr, {"tablename": tablename, "tablelist": tablelist})
        m = re.search(expr, sql, re.MULTILINE | re.IGNORECASE)
        if m:
            database = m.group("database")
            tablename = m.group("tablename")
            if not tablename:
                tablename = database
                database = "main"
        else:
            return (None, None)
        return (database.strip("[]"), tablename.strip("[]"))

    GetTablenameFromQuery = staticmethod(GetTablenameFromQuery)

    def tableExists(self, tablename):
        raise Exception("Not implemented here!")

    def escape(self, text):
        if isinstance(text, (str)):
            return text.decode("utf-8", "ignore")
        elif isinstance(text, (list, tuple)):
            return [self.escape(item) for item in text]
        else:
            return text

    def __prepare_query__(self, sql, env={}, verbose=False):
        """
        prepare the query
        remove comments and blank lines
        """
        comment1 = "//"
        comment2 = "#"
        sql = sql.replace("\r\n", "\n")
        sql = sql.replace("\r", "\n")
        sql = sql.replace(";", ";\n")
        lines = split(sql, "\n", "'\"")

        lines = [split(line, comment2, "'\"")[0] for line in lines]
        lines = [line.strip(" \t") for line in lines]

        lines = [line for line in lines if len(line) > 0 and not line.startswith(comment2)]
        ##for line in lines:
        #    print line
        #    print "---------"

        sql = " ".join(lines)

        env = self.__check_args__(env)

        return sql, env

    def __check_args__(self, env):
        """
        __check_args__
        """
        for key in env:
            value = env[key]
            if isstring(value) and "'" in value and not "POINT" in value:
                env[key] = value.replace("'", "''")
        return env


    def getCursorFor(self, query):
        """
        Returns a cursor from a query or tablename or cursor
        """
        if isinstance(query, (str, unicode)) and query.strip().upper().startswith("SELECT "):
            # It'a query
            return self.execute(query)
        elif isinstance(query, (str, unicode)):
            # maybe it's a tablename
            return self.execute("""SELECT * FROM [%s];""" % (query))
        else:
            # Probably it's a cursor
            return query

    def fast_execute(self, sql, commit=True, verbose=False):
        """
        Make a single query statement try protected
        Returns a cursor
        """
        cursor = self.__get_cursor__()
        if cursor:
            try:
                t1 = time.time()
                cursor = self.__get_cursor__()
                cursor.execute(sql)
                if commit:
                    self.commit()
                t2 = time.time()

                if verbose:
                    line = sql.encode('ascii', 'ignore').replace("\n", " ")
                    print "->%s:Done in (%.2f)s" % (line[:], (t2 - t1))
            except Exception, ex:
                if verbose:
                    line = sql
                    print "->%s...:No![%s]!" % (line[:], ex)
        return cursor


    def safe_execute(self, sql, commit=True, verbose=False):
        """
        Make a single query statement try protected
        Returns a cursor
        """
        retry = True
        cursor = self.__get_cursor__()
        if cursor:
            while retry:
                try:
                    t1 = time.time()
                    ## Try each command
                    cursor.execute(sql)
                    if commit:
                        self.commit()
                    t2 = time.time()

                    if verbose:
                        line = sql.encode('ascii', 'ignore').replace("\n", " ")
                        print "->%s:Done in (%.2f)s" % (line[:], (t2 - t1))

                    retry = False

                except sqlite.OperationalError as ex:
                    if ex.message == "database is locked":
                        print "locked sleep"
                        time.sleep(3)
                        print "Trying again"
                        retry = True
                    else:
                        retry = False
                        if verbose:
                            # line = sql.encode('ascii','ignore').replace("\n"," ")
                            line = sql
                            print "->%s...:No![%s]!" % (line[:], ex)
                except Exception as ex:
                    retry = False
                    if verbose:
                        # line = sql.encode('ascii','ignore').replace("\n"," ")
                        line = sql
                        print "->%s...:No![%s]!" % (line[:], ex)
        else:
            if verbose:
                line = sql.encode('ascii', 'ignore').replace("\n", " ")
                print "Cannot execute the command <%s> because the cursor is None." % line

        return cursor

    def execute(self, sql, environ={}, keepdims=True, commit=True, verbose=False):
        """
        Make a query statement list
        Returns a cursor
        """
        cursor = None
        sql, environ = self.__prepare_query__(sql, environ, verbose)

        sql = sformat(sql, environ)
        commands = split(sql, ";", "'\"")
        commands = [command.strip() + ";" for command in commands if len(command) > 0]

        for command in commands:
            cursor = self.safe_execute(command, commit=commit, verbose=verbose)

        if not keepdims:
            rows = []
            for row in cursor:
                rows.append(row)

            if len(rows) == 1:
                firstrow = rows[0]
                if len(firstrow) == 1:
                    return firstrow[0]
                return firstrow
            return rows

        return cursor


    def executeScalar(self, sql, environ={}, commit=True, verbose=False):
        """
        Make a query statetment
        Returns a value
        """
        cursor = self.execute(sql, environ, keepdims=True, commit=commit, verbose=verbose)
        if cursor:
            row = cursor.fetchone()
            return row[0] if row else None
        return None


    def executeMany(self, sql, environ={}, values=[], commit=True, verbose=False):
        """
        Make a query statetment
        Returns a cursor
        """
        cursor = self.__get_cursor__()
        line = sformat(sql, environ)
        try:
            t1 = time.time()
            # cursor.executemany(line, self.escape(values))
            cursor.executemany(line, values)
            if commit:
                self.commit()
            t2 = time.time()
            if verbose:
                line = line.encode('ascii', 'ignore').replace("\n", " ")
                print "->%s:Done in (%.2f)s" % (line[:], (t2 - t1))
        except sqlite.Error as ex:
            print("SqlException in <%s> id (%s)" % (line, ex))

    def executemany(self, sql, environ={}, values=[], commit=True, verbose=False):
        """
        executemany -  alias od executeMany
        """
        self.executeMany(sql, environ, values, commit, verbose)

    def commit(self):
        """
        Commit
        """
        if self.conn:
            self.conn.commit()

    def close(self, verbose=False):
        """
        Close the db connection
        """
        if self.conn:
            self.conn.close()

    def drop(self, tablename, verbose=False):
        """
        drop - a list of tables
        """
        for tablename in listify(tablename, ","):
            tablename = tablename.strip("[]")
            sql = """DROP TABLE IF EXISTS [{tablename}];DROP VIEW IF EXISTS [{tablename}];"""
            self.execute(sql, {"tablename": tablename}, verbose=verbose)

    def createTable(self, tablename, fieldlist, typelist=None, primarykeys=None, Temp=False, overwrite=False,
                    verbose=False):
        """
        Create a Table from field list
        """
        fieldlist = listify(fieldlist)
        typelist = listify(typelist, ",")
        primarykeys = listify(primarykeys)

        # print fieldlist,typelist,primarykeys
        typelist = [""] * len(fieldlist) if not typelist else typelist
        fieldnames = ["%s %s" % (fieldname, fieldtype) for (fieldname, fieldtype) in zip(fieldlist, typelist)]
        if primarykeys:
            fieldnames += ["""PRIMARY KEY(%s)""" % (",".join(primarykeys))]
        fieldnames = ",".join(fieldnames)

        temp = "TEMP" if Temp else ""
        tablename = tablename.strip("[]")
        env = {"tablename": tablename, "TEMP": temp, "fieldnames": fieldnames}
        if overwrite:
            self.drop(tablename, verbose)
        query = """CREATE {TEMP} TABLE IF NOT EXISTS [{tablename}]({fieldnames});"""
        self.execute(query, env, verbose=verbose)

        return tablename

    def importCsv(self, filename, tablename=None, primarykeys="", comments="", Temp=False, append=True,
                  nodata=["", "Na", "NaN", "--"], verbose=False):
        raise Exception("Not implemented here!")

    def importXls(self, filename, sheetname=None, Temp=False, nodata=["", "Na", "NaN", "--"], verbose=False):
        raise Exception("Not implemented here!")

    def toCsv(self, cursor, filename, sep=";", decimal="."):
        """
        Generate a csv file from cursor
        """
        try:
            cursor = self.getCursorFor(cursor)
            metadata = cursor.description
            columnnames = [item[0] for item in metadata]

            with open(filename, 'wb') as stream:
                writer = csv.writer(stream, dialect='excel', delimiter=sep, quotechar='"', quoting=csv.QUOTE_MINIMAL)
                line = columnnames
                writer.writerow(line)
                row = cursor.fetchone()
                while row:
                    row = [("%s" % (item if item != None else "")) for item in row]
                    if decimal == ",":
                        row = [item.replace(".", ",") for item in row]
                    writer.writerow(row)
                    row = cursor.fetchone()
        except Exception, ex:
            print "ToCsv Exception:%s" % ex

    def toExcel(self, cursor, filename="", sheetname=""):
        """
        Generate a excel file from sql query
        """
        cursor = self.getCursorFor(cursor)
        sheetname = (juststem(filename))[:31] if not sheetname else sheetname[:31]
        metadata = cursor.description
        columnnames = [item[0] for item in metadata]

        # Create or open the workbook
        wb = xlwt.Workbook()

        # Get an existing sheet or create a new one
        try:
            sheet = wb.add_sheet(sheetname)
        except:
            j = 0
            while wb.get_sheet(j).name.lower() != sheetname.lower():
                j += 1
            sheet = wb.get_sheet(j)

        # Write the header
        i = 0
        for j in range(len(columnnames)):
            sheet.write(i, j, columnnames[j])
        i = 1
        # For each row,column  write ...
        row = cursor.fetchone()
        while row:
            for j in range(len(row)):
                value = row[j]
                sheet.write(i, j, value)
            i += 1
            row = cursor.fetchone()
        wb.save(filename)










if __name__ == "__main__":
    workdir = justpath(__file__) + "/tests"
    chdir(workdir)
    from sqlitedb import *

    db = SqliteDB("test.sqlite")
    print db.executeScalar("SELECT 5,2,3,5 UNION SELECT 3,4,5,6;")
