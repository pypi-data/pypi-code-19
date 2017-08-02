import MySQLdb as mdb
import pandas as pd

from DataAccess.ConnectionConfigurationClient import get_connection_strings
from DataAccess.FileSystemIO import FileSystemIO


io = FileSystemIO()
connection_strings = io.read_json("DataAccess/connection_strings.json")


def connect_to_server(connection_name, database):
    """
    
    :param connection_name: 
    :param database: 
    :return: 
    """
    connection_info = get_connection_strings(connection_name, 'remote')
    cnx = mdb.connect(connection_info[0], connection_info[2], connection_info[3], database)
    return cnx

def close_connection(connection):
    """
    
    :param connection: 
    :return: 
    """
    connection.close()


def execute_query(connection, query):
    """
    
    :param connection: 
    :param query: 
    :return: 
    """
    cursor = connection.cursor()
    cursor.execute(query)
    result =  list(cursor)

    if len(result) > 0:
        field_names = [i[0] for i in cursor.description]
        return pd.DataFrame(data=result, columns=field_names)

    return pd.DataFrame()




