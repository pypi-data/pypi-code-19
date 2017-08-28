import time
import sys
from sqlalchemy import MetaData, Table
from sqlalchemy import create_engine, desc
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.pool import NullPool

from mylittlehelpers import time_bomb

import os


class TokenBox:

    def __init__(self, db_user, db_password, db_name, use_sqlite, metadata, **kwargs):
        """
        :param db_user (string): user of db login role (must be capable of creating a PG database)
        :param db_password (string): password of db login role
        :param db_name (string): name of database to be created/managed
        :param use_sqlite (bool): whether or not to use sqlite
        :param metadata (sqlalchemy.MetaData): metadata used in table definitions
        :param kwargs (sqlalchemy.Table): names of Tables and corresponding definitions
        """
        pg_conn_format = "postgresql://{user}:{password}@{host}:{port}/{database}"
        sqlite_conn_format = "sqlite:///{database}.db"
        pg_config_dict = {
            'user': db_user,
            'password': db_password,
            'host': 'localhost',
            'port': 5432,
        }
        self.use_sqlite = use_sqlite
        self.db_name = db_name
        self.connection_strings = {
            "pg_conn_uri_default": pg_conn_format.format(database='postgres', **pg_config_dict),
            "pg_conn_uri_new":  pg_conn_format.format(database=db_name, **pg_config_dict),
            "sqlite_conn_uri": sqlite_conn_format.format(database=db_name)
        }
        self.metadata = metadata
        self.table_definitions = {}

        for key, table in kwargs.items():
            assert(isinstance(table, Table), "All keyword argmuments must be an sqlalchemy.Table "
                                             "object.")
            self.table_definitions[key] = table

    def create_database(self):
        """
        Creates a database corresponding to the arguments passed during TokenBox initialization
        """
        if self.use_sqlite:
            return
        engine = create_engine(self.connection_strings["pg_conn_uri_default"])
        conn = engine.connect()
        conn.execute("COMMIT")
        conn.execute("CREATE DATABASE %s" % self.db_name)
        conn.close()
        print(f'{self.db_name} created successfully.')

    def destroy_database(self):
        """
        Destroys a database corresponding to the arguments passed during TokenBox initialization
        """
        time_bomb(5, action=f"Database named {self.db_name} will be destroyed", package=(print, ("",)))
        if self.use_sqlite:
            db_location = self.connection_strings["sqlite_conn_uri"].split("sqlite:///")[1]
            os.remove(db_location)
            print(f'\n{self.db_name} dropped successfully.')
            return
        pg_engine_default = create_engine(self.connection_strings["pg_conn_uri_default"])
        conn = pg_engine_default.connect()
        conn.execute("COMMIT")
        conn.execute("DROP DATABASE %s" % self.db_name)
        conn.close()
        print(f'{self.db_name} dropped successfully.')

    def get_token(self, table_name):
        """
        Gets the token from the specified table (there's only one in storage!)
        :param table_name:
        :return:
        """
        if self.use_sqlite:
            engine = create_engine(self.connection_strings["sqlite_conn_uri"])
            data = MetaData(engine)
            table = Table(table_name, data, autoload=True)
            conn = engine.connect()
            result = table.select().order_by(desc(f'{table_name}_pk')).execute()
            conn.close()
            for item in result:
                return item
        else:
            engine = create_engine(self.connection_strings["pg_conn_uri_new"], poolclass=NullPool)
            data = MetaData(engine)
            table = Table(table_name, data, autoload=True)
            conn = engine.connect()
            result = table.select().order_by(desc(f'{table_name}_pk')).execute()
            conn.close()
            for item in result:
                return item

    def update_token(self, table_name, **kwargs):
        """
        Updates (or inserts) the row into the specified table (there can only be one in storage!)
        :param table_name:
        :param kwargs:
        :return:
        """
        if self.use_sqlite:
            engine = create_engine(self.connection_strings["sqlite_conn_uri"])
        else:
            engine = create_engine(self.connection_strings["pg_conn_uri_new"], poolclass=NullPool)
        if not table_name in Inspector.from_engine(engine).get_table_names():
            self.table_definitions[table_name].create(bind=engine)
            data = MetaData(engine)
            table = Table(table_name, data, autoload=True)
            conn = engine.connect()
            i = table.insert()
            i.execute(**kwargs)
            conn.close()
        else:
            data = MetaData(engine)
            table = Table(table_name, data, autoload=True)
            conn = engine.connect()
            i = table.update().where(table.c[f'{table_name}_pk'] == self.get_token(table_name)[f'{table_name}_pk'])
            i.execute(**kwargs)
            conn.close()
