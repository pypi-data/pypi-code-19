from DataAccess.FileSystemIO import FileSystemIO

io = FileSystemIO()
connection_strings = io.read_json("DataAccess/connection_strings.json")

def get_connection_strings(connection_name, connection_type):
    """

    :param connection_name:
    :param connection_type:
    :return:
    """
    for connection_string in connection_strings['connections']:
        if connection_string['name'] == connection_name:
            return str(connection_string['endpoint.%s' % connection_type]), \
                   str(connection_string['port.%s' % connection_type]), \
                   str(connection_string['user']), \
                   str(connection_string['pwd'])