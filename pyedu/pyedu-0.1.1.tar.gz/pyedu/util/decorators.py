from functools import wraps
from flask import session, redirect, url_for, abort
from flask_login import current_user
from pyedu.models import User

def has_role(role):
    """

    :param role:
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # check if a user is logged in
            if not current_user.is_authenticated:
                return redirect(url_for('main.login'))
            if current_user.has_role('superuser'):
                return f(*args, **kwargs)
            elif not current_user.has_role(role):
                return abort(403)
            else:
                return f(*args, **kwargs)
        return decorated
    return decorator


def has_level(level):
    """

    :param level:
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('main.login'))
            if current_user.has_level(level):
                return f(*args, **kwargs)
            else:
                return abort(403)
        return decorated
    return decorator


