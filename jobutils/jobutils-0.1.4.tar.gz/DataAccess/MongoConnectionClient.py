from DataAccess import FileSystemIO
from pymongo import MongoClient
import platform

__author__ = "laurynas@joberate.com"

io = FileSystemIO.FileSystemIO()
connection_strings = io.read_json("DataAccess/connection_strings.json")

# Defines functions to access MongoDB connection string. Need to install uzys-elasticache-client in order to use local
# connection strings


def connect_to_database(connection_name, database, authentication_database='modelling'):
    """

    :param connection_name:
    :param database:
    :param authentication_database:
    :return:
    """
    host, port, user, pwd = get_connection_parameters(connection_name)
    client = MongoClient(host, port)
    client[authentication_database].authenticate(user, pwd)
    return client[database]


def connect_to_client(connection_name, authentication_database='modelling'):
    """

    :param connection_name:
    :param authentication_database:
    :return:
    """
    host, port, user, pwd = get_connection_parameters(connection_name)
    client = MongoClient(host, port)
    client[authentication_database].authenticate(user, pwd)
    return client


def get_connection_parameters(connection_name):
    """

    :return: host, port of MongoDB connection

    if 'job101' in get_pc_name().lower():
        return get_connection(connection_name, 'local')
    """
    return get_connection(connection_name, 'remote')


def get_pc_name():
    """

    :return: machine name
    """
    return platform.node().lower()


def get_connection(connection_name, connection_type):
    """

    :param connection_name:
    :param connection_type:
    :return:
    """
    for connection_string in connection_strings['connections']:
        if connection_string['name'] == connection_name:
            return connection_string['endpoint.%s' % connection_type], \
                   connection_string['port.%s' % connection_type], \
                   connection_string['user'], \
                   connection_string['pwd']
