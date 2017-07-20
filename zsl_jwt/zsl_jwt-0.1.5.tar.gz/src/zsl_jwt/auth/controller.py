"""
:mod:`zsl_jwt.controller`
-------------------------

Contains the login function.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import http
from builtins import *  # NOQA

from zsl import inject
from zsl.application.error_handler import ErrorResponse
from zsl.task.job_context import StatusCodeResponder
from zsl.task.job_context import add_responder
from zsl.task.task_decorator import json_output
from zsl.utils.http import get_http_status_code_value

from zsl_jwt.auth.service import AuthenticationService
from zsl_jwt.auth.service import StandardUserInformation  # NOQA
from zsl_jwt.auth.service import create_standard_user_information
from zsl_jwt.decorators import jwt_output

ERROR_CODE_INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
ERROR_MESSAGE_INVALID_CREDENTIALS = "Username and password can not be verified."


@inject(authentication_service=AuthenticationService)
def authenticate(username, password, authentication_service):
    # type: (str, str, AuthenticationService)->str
    """
    the "login" function, from the given username/password returns the jwt.

    :param username:
    :param password:
    :param authentication_service: Injected. Uses
           :class:`zsl_jwt.auth.service.AuthenticationService` to query
           the database.
    :return: error response if the credentials are invalid or jwt.
    """
    # type:(str, str, AuthenticationService)->Any
    if not authentication_service.verify_password(username, password):
        return _respond_with_error()

    return _respond_with_jwt(username, authentication_service)


@json_output
def _respond_with_error():
    # type: ()->ErrorResponse
    add_responder(StatusCodeResponder(get_http_status_code_value(http.client.FORBIDDEN)))
    return ErrorResponse(ERROR_CODE_INVALID_CREDENTIALS, ERROR_MESSAGE_INVALID_CREDENTIALS)


@jwt_output()
def _respond_with_jwt(username, authentication_service):
    # type:(str, AuthenticationService)->StandardUserInformation
    roles, user_object = authentication_service.get_user_information(username)
    return create_standard_user_information(username, roles, user_object).get_attributes()
