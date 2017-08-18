import inspect
import os
import re
import sys
import tempfile
import logging

if sys.version_info.major < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    ModuleNotFoundError = ImportError

import pandas.io.sql
try:
    import psycopg2
    import psycopg2.extras
except ModuleNotFoundError as e:
    psycopg2 = False

import lore
from lore.util import timer


logger = logging.getLogger(__name__)


class Connection(object):
    UNLOAD_PREFIX = os.path.join(lore.env.name, 'unloads')
    IAM_ROLE = os.environ.get('IAM_ROLE')
    
    def __init__(self, url):
        self.__url = url
        self.connect()

    def __enter__(self):
        self.adapter.autocommit = False
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.adapter.commit()
        else:
            self.adapter.rollback()
        self.adapter.autocommit = True

    def connect(self):
        logger.info(self.__url)
        if not psycopg2:
            logger.error('psycopg2 is not installed')
            return
        
        parsed = urlparse(self.__url)
        self.adapter = psycopg2.connect(
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
            connect_timeout=1
        )
        self.adapter.autocommit = True
        self.cursor = self.adapter.cursor(
            cursor_factory=psycopg2.extras.DictCursor)

    def close(self):
        self.adapter.close()

    def execute(self, sql=None, filename=None, **kwargs):
        self.__execute(self.__prepare(sql, filename, kwargs))

    def select(self, sql=None, filename=None, **kwargs):
        self.__execute(self.__prepare(sql, filename, kwargs))
        return self.cursor.fetchall()

    def unload(self, table, sql=None, filename=None, **kwargs):
        if sql is None and filename is None:
            filename = os.path.join(
                lore.env.root(), lore.env.project, 'extracts', table + ".sql")
            if not os.path.isfile(filename):
                sql = "SELECT * FROM " + table
            else:
                filename = table
        sql = self.__prepare(sql, filename, kwargs)
        sql = "UNLOAD ('" + sql.replace("'", "\\'") + "') "
        sql += "TO 's3://" + os.path.join(
                lore.io.bucket.name,
                self.UNLOAD_PREFIX,
                table,
                table
                ) + "' "
        
        if Connection.IAM_ROLE:
            sql += "IAM_ROLE '" + Connection.IAM_ROLE + "' "
        sql += "DELIMITER ',' ALLOWOVERWRITE ESCAPE"
        self.__execute(sql)

    def load(self, path, table=None, columns=None):
        if table is None:
            table = path

        for entry in lore.io.bucket.objects.filter(
            Prefix=os.path.join(self.UNLOAD_PREFIX, path)
        ):
            temp = tempfile.NamedTemporaryFile()
            with timer("SQL COPY: %s -> %s" % (entry.key, table)):
                lore.io.bucket.download_file(entry.key, temp.name)
            temp.seek(0)
            self.cursor.copy_from(temp, table, sep=',', columns=columns)

    def insert(self, sql, tuples):
        records_list_template = ','.join(['%s'] * len(tuples))
        sql = sql.format(records_list_template)
        sql = self.cursor.mogrify(sql, tuples).decode('utf-8')
        self.__execute(sql)

    def dataframe(self, sql=None, filename=None, **kwargs):
        sql = self.__prepare(sql, filename, kwargs)
        sql = self.__caller_annotation(stack_depth=2) + sql
        logger.debug(sql)
        with timer("SQL TIME:"):
            return pandas.io.sql.read_sql(sql=sql, con=self.adapter)

    def etl(self, table, to, **kwargs):
        self.unload(table, **kwargs)
        with to as transaction:
            transaction.execute("DELETE FROM " + table)
            transaction.load(table)
            transaction.execute("ANALYZE " + table)
        to.execute("ANALYZE " + table)

    def __prepare(self, sql, filename, bindings):
        if sql is None and filename is not None:
            filename = os.path.join(
                lore.env.root, lore.env.project, 'extracts', filename + ".sql")
            logger.debug("READ SQL FILE: " + filename)
            with open(filename) as file:
                sql = file.read()
        # support mustache style bindings
        sql = re.sub('\{(\w+?)\}', r'%(\1)s', sql)
        return self.cursor.mogrify(sql, bindings).decode('utf-8')

    def __execute(self, sql):
        sql = self.__caller_annotation() + sql
        logger.debug(sql)
        with timer("SQL TIME:"):
            self.cursor.execute(sql)

    def __caller_annotation(self, stack_depth=3):
        caller = inspect.stack()[stack_depth]
        if sys.version_info.major == 3:
            caller = (caller.function, caller.filename, caller.lineno)
        return "/* %s | %s:%d in %s */\n" % (os.environ.get(
            "ISC_SERVICE"), caller[1], caller[2], caller[0])
