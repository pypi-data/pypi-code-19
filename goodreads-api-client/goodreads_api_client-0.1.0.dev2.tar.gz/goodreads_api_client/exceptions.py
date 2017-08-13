# -*- coding: utf-8 -*-
"""
goodreads_api_client.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains goodreads_api_client's exceptions.
"""


class GoodreadsApiClientException(Exception):
    """Base exception"""


class OauthEndpointNotImplemented(GoodreadsApiClientException):
    """OAuth not yet supported by this library"""


class ExtraApiPermissionsRequired(GoodreadsApiClientException):
    """Must contact Goodreads for extra perms to use endpoint"""
