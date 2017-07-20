"""
:mod:`zsl_jwt.decorators`
-------------------------

The module provides a decorator which turns the function's output into a JWT.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA
from functools import wraps
from typing import Callable  # NOQA

from flask.config import Config
from zsl import inject
from zsl.task.task_decorator import json_output

from zsl_jwt.codec import encode
from zsl_jwt.configuration import DEFAULT_PROFILE_NAME


def jwt_output(profile=DEFAULT_PROFILE_NAME, debug=None):
    # type:(str, str)->Callable
    """
    Uses the returned dictionary as the JWT payload and returns
    a JSON with the token.

    :param profile: The JWT profile which is used.
    :param debug: The debug info - if true or the debug mode is on,
                  then the payload is in the returned JSON.
    :return: Dict with the 'token' key containing the created JWT.
    """

    def wrapper_function(f):
        @inject(config=Config)
        def get_config(config):
            # type: (Config)->Config
            return config

        @wraps(f)
        @json_output
        def wrapper(*args, **kwargs):
            payload = f(*args, **kwargs)
            d = {'token': encode(payload, profile=profile)}
            if debug or (debug is None and get_config().get('DEBUG', False)):
                d['payload'] = payload
            return d

        return wrapper

    return wrapper_function
