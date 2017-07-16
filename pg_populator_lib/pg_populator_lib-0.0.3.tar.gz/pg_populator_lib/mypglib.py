#!/usr/bin/env python3

# Author: Jose Antonio Quevedo <joseantonio.quevedo@gmail.com>
# 2017-07-09

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_conn(user, db_name="template1", host="localhost"):

    try:
        connect_str = "dbname='" + db_name + "' user='" + user + "' host='localhost'"

        conn = psycopg2.connect(connect_str)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    except:
        print("I am unable to connect to the database")

    return conn


def execute_query(cursor, query, error_code_expected=None):

    result = False
    try:
        cursor.execute(query)
        result = True
    except psycopg2.ProgrammingError as e:
        if e.pgcode != error_code_expected:
            print(e.pgerror)
            raise

    return result


def get_databases_names(cursor):

    query = 'SELECT d.datname as "Name" FROM pg_catalog.pg_database d ORDER BY 1;'
    execute_query(cursor, query)
    db_names = cursor.fetchall()

    if db_names:
        db_names = [x[0] for x in db_names]

    return db_names
