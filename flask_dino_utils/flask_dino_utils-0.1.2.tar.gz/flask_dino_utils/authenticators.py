from werkzeug.exceptions import Unauthorized, Forbidden
from flask import request
from functools import update_wrapper

ROLED_BASED_ACCESS = 1
MYSELF_BASED_ACCESS = 2
ASOCIATED_BASED_ACCESS = 3


def __get_user(UserModel, UserSchema, username, password):
    user = UserModel.query.filter(UserModel.username == str(username)).first()
    if user is None:
        raise Unauthorized("The user %s might not exist." % username)
    if password != user.password:
        raise Unauthorized("The password for user %s is incorrect" % username)
    return user


def require_credentials(access_provided, id_roles=None, associated_field_key=None, associated_field_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not isinstance(access_provided, list):
                access_provided = [access_provided]
            authenticated = False
            for access in access_provided:
            return func(*args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator