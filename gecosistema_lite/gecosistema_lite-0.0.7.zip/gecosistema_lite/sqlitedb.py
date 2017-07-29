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
# Name:        sqlitedb.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     26/07/2017
# -------------------------------------------------------------------------------
from databases import *
from datatypes import *


class SqliteDB(AbstractDB):

    def __init__(self, filename):
        """
        Constructor
        """
        AbstractDB.__init__(self, filename)
        self.conn.execute("PRAGMA synchronous=OFF")
        self.conn.execute("PRAGMA journal_mode=WAL")
        # self.conn.execute("PRAGMA cache_size=4000")


    def create_function(self, func, nargs, fname):
        """
        create_function
        """
        self.conn.create_function(func, nargs, fname)


    def create_aggregate(self, func, nargs, fname):
        """
        create_aggregate
        """
        self.conn.create_aggregate(func, nargs, fname)


    def __connect__(self):
        """
        Connect to the sqlite instance
        """
        try:
            self.conn = sqlite.connect(self.dsn)

        except sqlite.Error as err:
            print(err)
            self.close()


    def __del__(self):
        """
        Destructor
        """
        self.close()


    def GetTables(self):
        """
        Return a list with all tablenames
        """
        cur = self.execute("""SELECT tbl_name FROM
            (   SELECT * FROM sqlite_master      WHERE type IN ('table','view') UNION
                SELECT * FROM sqlite_temp_master WHERE type IN ('table','view') );""")
        res = []
        for row in cur:
            res.append(row[0])
        return res

    def GetFieldNames(self, tablename, ctype=""):
        """
        GetFieldNames
        """
        env = {"tablename": tablename.strip("[]")}
        sql = """PRAGMA table_info([{tablename}])"""
        cursor = self.execute(sql, env)
        if not ctype:
            return [name for (cid, name, ftype, notnull, dflt_value, pk) in cursor.fetchall()]
        else:
            return [name for (cid, name, ftype, notnull, dflt_value, pk) in cursor.fetchall() if (ftype in ctype)]

    def GetPrimaryKeys(self, tablename):
        """
        GetPrimaryKeys
        """
        env = {"tablename": tablename.strip("[]")}
        sql = """PRAGMA table_info([{tablename}])"""
        cursor = self.execute(sql, env)
        return [name for (cid, name, type, notnull, dflt_value, pk) in cursor.fetchall() if pk > 0]

    def tableExists(self, tablename):
        """
        Check if tablename exists
        Return a boolean
        """
        env = {"tablename": tablename.strip("[]")}
        count = self.executeScalar("""SELECT COUNT(*) FROM
            (   SELECT * FROM sqlite_master WHERE type='table'      AND tbl_name='{tablename}' UNION
                SELECT * FROM sqlite_temp_master WHERE type='table' AND tbl_name='{tablename}')""", env)
        return count > 0

    def insertMany(self, tablename, values, commit=True, verbose=False):
        m, n = len(values), len(values[0]) if values else 0
        env = {"tablename": tablename, "question_marks": ",".join(["?"] * n)}
        sql = """INSERT OR REPLACE INTO [{tablename}] VALUES({question_marks});"""
        self.executeMany(sql, env, values, commit, verbose)

    def createTableFromCSV(self, filename, tablename, append=False, sep=";", primarykeys="", Temp=False, nodata=["Na"],
                           verbose=False):
        """
        createTableFromCSV - make a read-pass to detect data fieldtype
        """
        primarykeys = listify(primarykeys)
        # ---------------------------------------------------------------------------
        #   Open the stream
        # ---------------------------------------------------------------------------
        with open(filename, "rb") as stream:
            # ---------------------------------------------------------------------------
            #   decode data lines
            # ---------------------------------------------------------------------------
            fieldnames = []
            fieldtypes = []
            n = 1
            line_no = 0
            header_line_no = 0
            csvreader = csv.reader(stream, delimiter=sep, quotechar='"')

            for line in csvreader:
                line = [unicode(cell, 'utf-8-sig') for cell in line]
                if len(line) < n:
                    # skip empty lines
                    pass
                elif not fieldtypes:
                    n = len(line)
                    fieldtypes = [''] * n
                    fieldnames = line
                    header_line_no = line_no
                else:
                    fieldtypes = [SQLTYPES[min(SQLTYPES[item1], SQLTYPES[item2])] for (item1, item2) in
                                  zip(sqltype(line, nodata=nodata), fieldtypes)]

                line_no += 1

            self.createTable(tablename, fieldnames, fieldtypes, primarykeys, overwrite=not append, verbose=True)
            return (fieldnames, fieldtypes, header_line_no)

    def importCsv(self, filename, tablename=None,
                  sep=";", comments="",
                  primarykeys="", append=False, Temp=False,
                  nodata=["", "Na", "NaN", "-", "--", "N/A"], verbose=False):

        tablename = tablename if tablename else juststem(filename)
        (fieldnames, fieldtypes, header_line_no) = self.createTableFromCSV(filename, tablename, append, sep,
                                                                           primarykeys, Temp, nodata, verbose)
        # ---------------------------------------------------------------------------
        #   Open the stream
        # ---------------------------------------------------------------------------
        data = []
        n = len(fieldnames)
        line_no = 0
        with open(filename, "rb") as stream:
            csvreader = csv.reader(stream, delimiter=sep, quotechar='"')

            for line in csvreader:
                if line_no > header_line_no:
                    line = [unicode(cell, 'utf-8-sig') for cell in line]
                    if len(line) == n:
                        data.append(line)
                line_no += 1

            values = [parseValue(row) for row in data]
            self.insertMany(tablename, values, verbose=verbose)

    def importNumpy(self, data, tablename, append=True, Temp=False,
                    nodata=["", "Na", "NaN", "-", "--", "N/A"],
                    verbose=False):

        m, n = data.shape
        values = [parseValue(data[i]) for i in range(m)]
        self.insertMany(tablename, values, verbose=verbose)

    def excel2Numpy(self, sheet, justvalues=False):
        """
        excel2Numpy - load excel in to matrix of cell
        """
        cellMatrix = []
        m, n = sheet.nrows, sheet.ncols
        for i in range(m):
            if justvalues:
                row = sheet.row_values(i, start_colx=0, end_colx=None)
            else:
                row = sheet.row_slice(i, start_colx=0, end_colx=None)
            cellMatrix.append(row)
        # ------------------------------------------------------
        # Following lines explodes merged cells
        for (i0, i1, j0, j1) in sheet.merged_cells:
            for i in xrange(i0, i1):
                for j in xrange(j0, j1):
                    # cell (rlo, clo) (the top left one) will carry the data
                    # and formatting info; the remainder will be recorded as
                    # blank cells, but a renderer will apply the formatting info
                    # for the top left cell (e.g. border, pattern) to all cells in
                    # the range.
                    cell = sheet.cell(i0, j0).value if justvalues else sheet.cell(i0, j0)
                    cellMatrix[i][j] = cell
                    # ------------------------------------------------------
        cellMatrix = np.array(cellMatrix)

        return np.array(cellMatrix)

    def createTableFromXls(self, filename, sheetname, append=False, primarykeys="",
                           Temp=False,
                           nodata=["", "Na", "NaN", "-", "--", "N/A"],
                           verbose=False):
        """
        createTableFromXls - make a read-pass to detect data fieldtype
        """
        primarykeys = listify(primarykeys)
        data = []

        with xlrd.open_workbook(filename) as wb:
            sheet = wb.sheet_by_name(sheetname)
            cellMatrix = self.excel2Numpy(sheet)
            vMatrix = np.empty_like(cellMatrix)
            m, n = cellMatrix.shape
            fieldtypes = [9999] * n
            for i in range(m):
                vMatrix[i, :] = xlsvalue(cellMatrix[i][:], nodata)
                fieldtypes = [SQLTYPES[min(SQLTYPES[item1], item2)] for item1, item2 in
                              zip(sqltype(cellMatrix[i][:], nodata=nodata), fieldtypes)]

            fieldnames = ["field%d" % j for j in range(n)]

            self.createTable(sheetname, fieldnames, fieldtypes, primarykeys, overwrite=not append, verbose=True)
            return (fieldnames, fieldtypes, 0)

    def guessPrimaryKey(self, filename, sheetname, nodata=["", "Na", "NaN", "-", "--", "N/A"]):
        """
        createTableFromXls - make a read-pass to detect data fieldtype
        """
        with xlrd.open_workbook(filename) as wb:
            sheet = wb.sheet_by_name(sheetname)
            cellMatrix = self.excel2Numpy(sheet)
            m, n = cellMatrix.shape

            vMatrix = np.empty_like(cellMatrix)
            for i in range(m):
                vMatrix[i, :] = xlsvalue(cellMatrix[i, :], nodata)

            candidate = []
            for j in range(n):
                column = vMatrix[:, j]
                vDistinct = np.unique(column)
                # check distinct values an null
                if len(vDistinct) == len(column):
                    findnone = False
                    for jj in range(len(vDistinct)):
                        if vDistinct[jj] is None:
                            findnone = True
                            break
                    if not findnone:
                        candidate += [j]

            print candidate

    def importXls(self, filename, sheetname=None,
                  primarykeys="",
                  append=False,
                  Temp=False,
                  nodata=["", "Na", "NaN", "-", "--", "N/A"],
                  verbose=False):
        """
        importXls
        """

        data = []
        cellMatrix = []

        with xlrd.open_workbook(filename) as wb:
            for sheet in wb.sheets():
                if sheetname is None or lower(sheet.name) == lower(sheetname):
                    tablename = sheet.name
                    (fieldnames, fieldtypes, header_line_no,) = self.createTableFromXls(filename, sheet.name,
                                                                                        append=append,
                                                                                        primarykeys=primarykeys,
                                                                                        Temp=Temp,
                                                                                        nodata=nodata,
                                                                                        verbose=verbose)

                    cellMatrix = self.excel2Numpy(sheet)
                    m, n = cellMatrix.shape
                    for i in range(m):
                        data.append(xlsvalue(cellMatrix[i][:], nodata))

                    self.insertMany(tablename, data, verbose=verbose)

    def From(filename, sheetname=None, nodata=["", "Na", "NaN", "-", "--", "N/A"]):
        """
        Initialize db from filename or sql
        """
        if isfiletype(filename, "db,sqlite"):
            return SqliteDB(filename)

        elif isfilexls(filename, check_if_exists=True):
            db = SqliteDB(forceext(filename, "sqlite"))
            db.importXls(filename, sheetname, Temp=False, nodata=nodata)
            return db

        elif isquery(filename):
            # get from a simple sql string
            filexls, sheetname = SqliteDB.GetTablenameFromQuery(filename)
            if file(filexls):
                print forceext(filexls, "sqlite")
                db = SqliteDB(forceext(filexls, "sqlite"))
                db.importXls(filexls, sheetname, Temp=False, nodata=nodata)
                return db

        print filename, isquery(filename)
        return None

    From = staticmethod(From)


if __name__ == "__main__":
    workdir = justpath(__file__) + "/tests"
    chdir(workdir)
    filename = "test.sqlite"
    filexls = "test.xlsx"
    db = SqliteDB.From(filename)

    db.guessPrimaryKey(filexls, "test")

    db.close()















































if __name__ == "__main__":
    workdir = r"C:\Users\vlr20\Desktop"
    chdir(workdir)
    db = SqliteDB("data.sqlite")
    db.createTable("helloworld", "id,descr")
    db.close()
