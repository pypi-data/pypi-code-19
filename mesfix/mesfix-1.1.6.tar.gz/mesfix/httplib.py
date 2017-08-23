from base64 import b64decode
import requests
import json

_HEADER_NAME = 'user-data'


def check_user_data_header(request):
    """
    Checks if the 'user-data' header is present in the request.
    :param request: Request object.
    :return:
    """
    return request.headers.get(_HEADER_NAME)


def decode_user_data(request):
    """
    Extracts the user information that comes in the User-Data header.
    :param request: Request object.
    :return: User identifier, profile identifier and a list of the user's privileges.
    """

    if not check_user_data_header(request):
        raise Exception("%s header wasn't found" % _HEADER_NAME)

    # request must be a flask.request proxy object.
    header_data = request.headers.get(_HEADER_NAME)

    # We already know data comes encoded in Base64, so we proceed to decode it.
    decoded_data = json.loads(b64decode(header_data.encode('ascii')).decode('ascii'))

    if {'userId', 'profileId', 'roles', 'entityId'} != set(decoded_data.keys()):
        raise Exception("Invalid data")

    ans_tpl = []

    # This one-line function fetch a key from the dictionary if exist
    # otherwise, it returns the empty string as result
    this_or_none = lambda x: decoded_data[x] if x in decoded_data else ''

    ans_tpl.append(this_or_none('userId'))          # Get userId from the header if exist, otherwise, get ''
    ans_tpl.append(this_or_none('profileId'))       # Get profileId from the header if exist, otherwise, get ''
    ans_tpl.append(this_or_none('roles'))           # Get roles from the header if exist, otherwise, get ''
    ans_tpl.append(this_or_none('entityId'))        # Get entityId from the header if exist, otherwise, get ''
    ans_tpl.append(this_or_none('transactionId'))   # Get transactionId from the header if exist, otherwise, get ''

    return tuple(ans_tpl)
