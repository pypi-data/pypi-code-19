#!/usr/bin/env python3

# Author: Jose Antonio Quevedo <joseantonio.quevedo@gmail.com>
# 2017-07-09

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .config import *


def get_conn(user=DB_USER, db_name="postgres", host="localhost"):
    '''Returns an active database connection'''
    conn = None
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


def create_db(cursor, db_name):
    '''Creates a new database in the PostfreSQL service.


    Parameters
    ----------
    cursor : psycopg2.extensions.connection
        Instance of PostgreSQL connection.
    db_name : str
        Name of the database we are going to create.

    Returns
    -------
    bool
        True if the query was properly run.

    '''

    query = 'CREATE DATABASE ' + db_name
    # if pgcode == '42P04' then the database already exists
    return execute_query(cursor, query, error_code_expected='42P04')


def create_table(cursor, table_name):
    '''Creates a new table in the database pointed by cursor.'''

    query = """CREATE TABLE """ + table_name + """ (column_name char(40));"""
    # if pgcode == '42P04' then the table already exists
    return execute_query(cursor, query, error_code_expected='42P07')


def get_databases_names(cursor, db_prefix=DB_PREFIX):

    query = 'SELECT d.datname as "Name" FROM pg_catalog.pg_database d ORDER BY 1;'
    execute_query(cursor, query)
    db_names = cursor.fetchall()

    if db_names:
        db_names = [x[0] for x in db_names if db_prefix in x[0]]

    return db_names


# Next are massive create/insert/delete functions"

def clean_all_dbs(db_prefix=DB_PREFIX):
    '''Delete all databases created by this tool.'''

    with get_conn(DB_USER) as conn:
        with conn.cursor() as cursor:
            dbs = get_databases_names(cursor)
            for db_name in dbs:
                query = "drop database " + db_name + ";"
                cursor.execute(query)


def insert_rows(cursor, table_name, num_rows):
    '''Insert a num_rows of rows in the table stored in
    the database pointed by cursor'''

    if num_rows == 0:
        return True

    # Note: we join all the values in a query, because it is faster than
    # inserting a lot of queries with cursor.executemany()
    values = '),('.join(str(x) for x in range(num_rows))
    query = """INSERT INTO """ + table_name + """ VALUES (""" + values + """);"""
    return execute_query(cursor, query, error_code_expected=None)


def create_databases(num_db, db_prefix=DB_PREFIX):
    '''Creates a num_db amount of databases'''

    dbs_created = 0

    with get_conn(DB_USER) as conn:
        with conn.cursor() as cursor:
            for db_i in range(num_db):
                db_name = db_prefix + str(db_i)
                if create_db(cursor, db_name):
                    dbs_created += 1

    return dbs_created


def create_num_tables_with_data(cursor, num_tables, num_rows, table_prefix=TABLE_PREFIX):
    '''Creates a num_rows of rows in the first num_tables tables.'''

    tables_created = 0
    rows_inserted = 0

    for table_i in range(num_tables):
        table_name = table_prefix + str(table_i)

        # Create_table
        if create_table(cursor, table_name):
            tables_created += 1

        # insert rows
        if insert_rows(cursor, table_name, num_rows):
            # TODO: get the real amount of inserted rows from insert_rows().
            # We don't really need it for this exercise as the tables don't have any
            # primary or foreign key.
            rows_inserted += num_rows

    return tables_created, rows_inserted
