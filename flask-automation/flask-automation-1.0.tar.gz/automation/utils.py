from datetime import datetime
from functools import wraps
from flask import request, Response

try:
    from secrets import basic_auth_username, basic_auth_password
except ImportError:
    pass


def check_auth(username, password):
    """This function is called to check if a username password combination is valid."""
    return username == basic_auth_username and password == basic_auth_password

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def dictionarize(cursor, page_size=None):
    """
    Transforms a query result into a dictionary based on the table description

    :param cursor: cursor containing the resultset
    :param page_size: If set, the method expects a page of results. If the resultset is larger than page_size then the
    extra records are thrown away and a 'more' flag is set to true.
    :return: dictionary based on the table description
    """
    json_result = {'results': []}
    table_description = cursor.description

    def build(a_result):
        temp_result = {}
        for i in range(0, len(table_description)):
            temp_result[table_description[i][0]] = a_result[i]
        json_result['results'].append(temp_result)

    if page_size:
        json_result['more'] = False

    for index, result in enumerate(cursor.fetchall()):
        if page_size:
            if index >= page_size:
                json_result['more'] = True
            else:
                build(result)
        else:
            build(result)

    return json_result

