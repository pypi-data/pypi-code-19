import hashlib
from datetime import datetime
import sys
import boto3
import re
import six
import os

import psycopg2

from akagi.data_source import DataSource
from akagi.data_file_bundles import LocalDataFileBundle, S3DataFileBundle
from akagi.log import logger
from akagi.utils import normalize_path


class RedshiftDataSource(DataSource):
    '''RedshiftDataSource replesents a set of row data as a result of query param.
    It uses UNLOAD command and intermediate Amazon S3 bucket.
    '''
    def __init__(self, query_str, bucket_name=None, prefix=None, db_conf={}, no_cache=False):
        self._query_str = query_str
        self.__bucket_name = bucket_name
        self.__prefix = prefix
        self.__db_conf = db_conf
        self.__pgpass = None
        self._no_cache = no_cache

        if self.exists_local():
            self.bundle = LocalDataFileBundle(self._local_cache_dir)
        else:
            self.bundle = None

    def __iter__(self):
        if self.bundle is None:
            self._setup_bundle()

        return iter(self.bundle)

    def _setup_bundle(self):
        query = UnloadQuery(self._query_str, self._bucket_name, self._prefix)

        logger.debug("Executing query on Redshift")
        logger.debug("\n" + query.body + "\n")  # avoid logging unload query since it has raw credentials inside
        self._cursor.execute(query.sql)
        logger.debug("Finished")

        self.bundle = S3DataFileBundle(self._bucket_name, self._prefix)

        if not self._no_cache:
            self.save()
            self.bundle = LocalDataFileBundle(self._local_cache_dir)

    @property
    def _connection(self):
        return psycopg2.connect(**self._db_conf)

    @property
    def _cursor(self):
        return self._connection.cursor()

    @property
    def _db_conf(self):
        return {
            'host':
            self.__db_conf.get('host') or os.getenv('REDSHIFT_DB_HOST', self._pgpass['db_host']),
            'user':
            self.__db_conf.get('user') or os.getenv('REDSHIFT_DB_USER', self._pgpass['db_user']),
            'dbname':
            self.__db_conf.get('dbname') or os.getenv('REDSHIFT_DB_NAME', self._pgpass['db_name']),
            'password':
            self.__db_conf.get('password') or os.getenv('REDSHIFT_DB_PASS', self._pgpass['db_pass']),
            'port':
            self.__db_conf.get('port') or os.getenv('REDSHIFT_DB_PORT', self._pgpass['db_port'])}

    @property
    def _pgpass(self):
        if self.__pgpass is None:
            self.__pgpass = {}

            with open(os.path.expanduser(os.path.join('~', '.pgpass'))) as f:
                args = [s.strip() for s in f.read().split(':')]

                if len(args) == 5:
                    (
                        self.__pgpass['db_host'], self.__pgpass['db_port'],
                        self.__pgpass['db_name'], self.__pgpass['db_user'],
                        self.__pgpass['db_pass']) = args

        return self.__pgpass

    def __exit__(self, *exc):
        self.bundle.clear()
        return False

    @property
    def _hex_hash(self):
        return hashlib.sha256(self._query_str.encode('utf-8')).hexdigest()

    @property
    def _prefix(self):
        if self.__prefix is None:
            self.__prefix = os.path.join(
                os.getenv('AKAGI_UNLOAD_PREFIX', 'akagi_unload'),
                datetime.utcnow().strftime("%Y%m%d_%H%M%f"))

        return self.__prefix

    @property
    def _bucket_name(self):
        if self.__bucket_name is None:
            try:
                self.__bucket_name = os.environ['AKAGI_UNLOAD_BUCKET']
            except KeyError:
                logger.error('hoge')
                sys.exit(1)

        return self.__bucket_name


class Query(object):
    def __init__(self, body):
        self._body = body

    def wrap(self, query):
        raise NotImplementedError

    @property
    def body(self):
        if six.PY2:
            return self._body.decode('utf-8')
        else:
            return self._body

    def __str__(self):
        return self.body


class UnloadQuery(Query):
    def __init__(self, body, bucket_name, prefix, sort=False):
        super(UnloadQuery, self).__init__(body)

        self._bucket_name = bucket_name
        self._prefix = prefix
        self._sort = sort

    @property
    def sql(self):
        return """
unload ('%(query)s')
to '%(bundle_url)s'
credentials '%(credential_string)s'
gzip
allowoverwrite
parallel %(enable_sort)s
delimiter ',' escape addquotes
            """ % ({
            'query': re.sub(r"'", "\\\\'", self.body),
            'bundle_url': self._s3_url,
            'credential_string': self._credential_string,
            'enable_sort': "on" if self._sort else "off"})

    @property
    def _s3_url(self):
        loc = "%(bucket_name)s/%(prefix)s" % ({
            'bucket_name': self._bucket_name,
            'prefix': self._prefix})
        loc = normalize_path(loc)

        return "s3://%(loc)s" % locals()

    @property
    def _credential_string(self):
        credentials = []

        if self._credential is not None:
            if self._credential.access_key:
                credentials.append("aws_access_key_id=%s" % (self._credential.access_key))

            if self._credential.secret_key:
                credentials.append("aws_secret_access_key=%s" % (self._credential.secret_key))

            if self._credential.token:
                credentials.append("token=%s" % (self._credential.token))

        return ';'.join(credentials)

    @property
    def _credential(self):
        session = boto3.session.Session()
        return session.get_credentials()
