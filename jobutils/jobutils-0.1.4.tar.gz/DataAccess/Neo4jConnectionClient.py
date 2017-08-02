from DataAccess import FileSystemIO
from py2neo import Graph

io = FileSystemIO.FileSystemIO()
connection_strings = io.read_json("DataAccess/connection_strings.json")


# Defines functions to access Neo4j connection string.



def connect_to_database(connection_name, connection_type):
    """

    :param connection_name:
    :param connection_type:
    :return:
    """
    prefix, host, port, user, pwd = get_connection_parameters(connection_name, connection_type)
    client = Graph(prefix + user + ":" + pwd + "@" + host + ":" + str(port))
    return client


def get_connection_parameters(connection_name, connection_type):
    """

    :param connection_name:
    :param connection_type:
    :return: prefix, host, port, user, pwd of neo4j connection
    """
    for connection_string in connection_strings['connections']:
        if connection_string['name'] == connection_name:
            return connection_string['prefix.%s' % connection_type], \
                   connection_string['endpoint.%s' % connection_type], \
                   connection_string['port.%s' % connection_type], \
                   connection_string['user'], \
                   connection_string['pwd']


