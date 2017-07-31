import MySQLdb
import json
import threading


def connect_to_db(conn_dict):
    if not hasattr(connect_to_db, 'connections'):
        connect_to_db.connections = {}
    conn_dict_key = json.dumps(conn_dict, sort_keys=True)
    conn_dict_key = "{}-{}".format(conn_dict_key, threading.current_thread())
    connection = connect_to_db.connections.get(conn_dict_key)
    if not connection:
        db = conn_dict.get('db', '')
        user = conn_dict['user']
        passwd = conn_dict.get('passwd', '')
        host = conn_dict['host']
        port = conn_dict.get('port')
        connection = MySQLdb.connect(
            host=host, user=user, passwd=passwd, port=port, db=db
        )
        connect_to_db.connections[conn_dict_key] = connection
    return connection


def create_table_statement_from_table(table_name, conn_dict):
    sql = "SHOW CREATE TABLE {0}".format(table_name)
    return get_sql_result(sql, conn_dict)[0][1]


def get_sql_result(sql, conn_dict):
    db = connect_to_db(conn_dict)
    cur = db.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    db.commit()
    return results


def execute_sql(sql, conn_dict, params=None):
    db = connect_to_db(conn_dict)
    cur = db.cursor()
    cur.execute(sql, params)
    db.commit()


def show_databases(target_db_conn_dict):
    databases = ()
    conn_dict = _strip_name_from_conn_dict(target_db_conn_dict)
    for row in get_sql_result('SHOW DATABASES', conn_dict):
        databases = databases + row
    return databases


def list_tables(conn_dict):
    return [i[0] for i in get_sql_result(
        "show full tables where Table_Type = 'BASE TABLE';", conn_dict
    )]


def _strip_name_from_conn_dict(conn_dict):
    return {
        key: value for (key, value) in conn_dict.iteritems()
        if key != 'db'
    }


def drop_database(target_db_conn_dict):
    db_name = target_db_conn_dict['db']
    print("Dropping the database {0}.".format(db_name))
    conn_dict = _strip_name_from_conn_dict(target_db_conn_dict)
    execute_sql(
        "DROP DATABASE IF EXISTS {0};".format(db_name), conn_dict
    )


def create_database(target_db_conn_dict):
    db_name = target_db_conn_dict['db']
    print("Creating the database {0}.".format(db_name))
    conn_dict = _strip_name_from_conn_dict(target_db_conn_dict)
    execute_sql(
        "CREATE DATABASE IF NOT EXISTS {0};".format(db_name), conn_dict
    )
    execute_sql(
        "USE {0};".format(db_name), conn_dict
    )


def drop_and_create(target_db_conn_dict):
    print "Dropping and creating the database {0}.".format(
        target_db_conn_dict['db']
    )
    drop_database(target_db_conn_dict)
    create_database(target_db_conn_dict)


def convert_to_query_ready_string(sql_result):
    list_string = str([i[0] for i in sql_result if i[0] is not None])
    return list_string.replace('[', '(').replace(']', ')').replace('L', '')


def get_foreign_keys(source_db_conn_dict, table_name=None):
    where_statement = "WHERE REFERENCED_TABLE_SCHEMA = '{0}'".format(
        source_db_conn_dict['db']
    )
    if table_name:
        where_statement = "{0} AND REFERENCED_TABLE_NAME = '{1}'".format(
            source_db_conn_dict['db'], table_name
        )
    sql = """
        SELECT
          TABLE_NAME,
          COLUMN_NAME,
          CONSTRAINT_NAME,
          REFERENCED_TABLE_NAME,
          REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE {0};
    """.format(where_statement)
    return get_sql_result(sql, source_db_conn_dict)
