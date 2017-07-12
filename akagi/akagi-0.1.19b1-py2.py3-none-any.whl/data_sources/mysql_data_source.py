import csv
import hashlib
import os
import six

import MySQLdb

from akagi.data_source import DataSource
from akagi.data_file_bundles import LocalDataFileBundle
from akagi.log import logger


class MySQLDataSource(DataSource):
    '''MySQLDataSource replesents a set of row data as a result of query param.
    '''

    def __init__(self, query, db_conf={}, no_cache=False, keep_connection=False):
        self.query = query
        self.__db_conf = db_conf
        self.__connection = None
        self._keep_connection = keep_connection
        self._no_cache = no_cache

        if self.exists_local():
            self.bundle = LocalDataFileBundle(self._local_cache_dir)
        else:
            self.bundle = None

    @property
    def _connection(self):
        if self._keep_connection:
            if self.__connection is None:
                self.__connection = MySQLdb.connect(**self._db_conf)

            return self.__connection
        else:
            return MySQLdb.connect(**self._db_conf)

    def _setup_bundle(self):
        self.__result = []
        c = self._connection.cursor()
        logger.debug("Executing query...")
        c.execute(self.query)
        logger.debug("Finished.")

        rows = c.fetchall()

        tmp_csv_path = os.path.join('/tmp', 'akagi', self._hex_hash) + '.csv'
        tmp_csv_dir = os.path.dirname(tmp_csv_path)

        if not os.path.isdir(tmp_csv_dir):
            os.makedirs(tmp_csv_dir, mode=0o755)

        with open(tmp_csv_path, 'w') as f:
            csv.writer(f).writerows(rows)

            self.bundle = LocalDataFileBundle(tmp_csv_dir, file_format='csv')

        if not self._no_cache:
            self.save()
            self.bundle = LocalDataFileBundle(self._local_cache_dir)

    def __iter__(self):
        if self.bundle is None:
            self._setup_bundle()

        return iter(self.bundle)

    @property
    def _tmp_csv_path(self):
        return os.path.join('/tmp')

    @property
    def _db_conf(self):
        conf = {
            'host':
            self.__db_conf.get('host') or os.getenv('MYSQL_DB_HOST', 'localhost'),
            'user':
            self.__db_conf.get('user') or os.getenv('MYSQL_DB_USER'),
            'passwd':
            self.__db_conf.get('password') or os.getenv('MYSQL_DB_PASS'),
            'db':
            self.__db_conf.get('db') or os.getenv('MYSQL_DB_NAME'),
            'port':
            self.__db_conf.get('port') or os.getenv('MYSQL_DB_PORT', 3306),
            'unix_socket':
            self.__db_conf.get('unix_socket') or os.getenv('MYSQL_DB_SOCKET')}

        return {k: v for k, v in six.iteritems(conf) if v is not None}

    @property
    def _hex_hash(self):
        return hashlib.sha256(self.query.encode('utf-8')).hexdigest()
