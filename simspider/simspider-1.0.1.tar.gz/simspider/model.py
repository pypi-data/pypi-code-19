
class ContainerBase:
    """数据存储接口"""

    def newTableAndLabels(self, table, labels):
        """新建一张表与字段"""

    def setTable(self, table):
        """设置一张已有的表"""

    def put(self, data):
        """向表尾追加一列数据"""


class CsvContainer:
    """csv容器"""

    def __init__(self, databasedir, sep=","):
        import os
        self.ddir = os.getcwd().replace('\\', '/') + "/" + databasedir
        if not os.path.exists(self.ddir):
            os.makedirs(self.ddir)
        self.fp = None
        self.sep = sep

    def __del__(self):
        if self.fp:
            self.fp.close()

    def newTableAndLabels(self, table, labels, encoding="utf-8"):
        self.table = table
        self.fp = open(self.ddir + '/' + table +
                       '.csv', 'a', encoding=encoding)
        self.fp.write(self.sep.join(labels) + '\n')

    def setTable(self, table, encoding='utf-8'):
        self.table = table
        if not os.path.exists(self.ddir + '/' + table + '.csv'):
            raise Exception("请先设置表！")
            return
        self.fp = open(self.ddir + '/' + table +
                       '.csv', 'a', encoding=encoding)

    def put(self, data):
        self.fp.write(self.sep.join(data) + '\n')


class Sqlite3Container:
    """sqlite容器"""

    def __init__(self, database):
        import sqlite3
        self.conn = sqlite3.connect(database)

    def __del__(self):
        self.conn.close()

    def newTableAndLabels(self, table, labels):
        self.table = table
        sql = "create table " + table + "("
        for i in labels[:-1]:
            sql += (i + " text,")
        sql += (labels[-1] + " text)")
        self.conn.execute(sql)
        self.conn.commit()

    def setTable(self, table):
        self.table = table

    def put(self, data):
        sql = "insert into " + self.table + " values('"
        for i in data[:-1]:
            sql += (i + "','")
        sql += (data[-1] + "')")
        self.conn.execute(sql)
        self.conn.commit()


class MysqlContainer:
    """MySql容器"""

    def __init__(self, user, pwd, database, host="127.0.0.1", port=3306, charset="utf8mb4"):
        from pymysql import connect
        self.database = database
        self.conn = connect(host=host, port=port, user=user, db=database,
                            password=pwd, charset=charset)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close
        self.conn.close()

    def newTableAndLabels(self, table, labels):
        self.table = table
        sql = "create table " + table + "("
        for i in labels[:-1]:
            sql += (i + " text,")
        sql += (labels[-1] + " text)")
        self.cur.execute(sql)
        self.conn.commit()

    def setTable(self, table):
        self.table = table

    def put(self, data):
        sql = "insert into " + self.table + " values('"
        for i in data[:-1]:
            sql += (i + "','")
        sql += (data[-1] + "')")
        self.cur.execute(sql)
        self.conn.commit()

if __name__ == "__main__":
    cs = MysqlContainer(user='root', pwd='root', database="test")
    cs.newTableAndLabels('uio', ['1th', '2th', '3th', '4th'])
    cs.put(["sd", "sd", "cv", "sd"])
    cs.put(["3", "6", "7", "2"])
