"""
:mod:`zsl_jwt.configuration`
-------------------------

The configuration of the authentication.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA


class AuthConfiguration(object):
    """
    Auth module configuration. It holds the string identifying the
    authentication service.
    """

    def __init__(self, authentication_service_class):
        # type: (str)->None
        self._authentication_service_class = authentication_service_class

    @property
    def authentication_service_class(self):
        # type:()->str
        """
        The string identifying the class implementing the
        :class:`zsl_jwt.auth.service.AuthenticationService` which is used
        for login controller.
        """
        return self._authentication_service_class
