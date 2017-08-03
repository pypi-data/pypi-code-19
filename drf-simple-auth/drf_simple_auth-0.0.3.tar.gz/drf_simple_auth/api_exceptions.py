from __future__ import absolute_import, unicode_literals

from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidEmailOrPasswordAPIException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid email or password.  Please try logging in again.'


class InvalidEmailUsernameAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Please provide a valid email address.'


class UsernameAlreadyTakenAPIException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Username already taken'
