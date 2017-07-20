"""
:mod:`zsl_jwt.auth.module`
--------------------------

This ZSL module reads the auth configuration and provides
:class:`zsl_jwt.auth.configuration.AuthConfiguration` and an instance of
:class:`zsl_jwt.auth.service.AuthenticationService`.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA

from flask.config import Config
from injector import Module
from injector import provides
from zsl import inject
from zsl.utils.import_helper import fetch_class

from zsl_jwt.auth.configuration import AuthConfiguration
from zsl_jwt.auth.service import AuthenticationService


class AuthModule(Module):
    AUTH_CONFIG_NAME = 'AUTH'

    @provides(AuthConfiguration)
    @inject(config=Config)
    def provide_jwt_configuration(self, config):
        # type: (Config) -> AuthConfiguration
        """
        Returns the AuthConfiguration.

        :param config: Injected. Configuration object
        :return: Current authentication/authorization configuration.
        """
        return config[AuthModule.AUTH_CONFIG_NAME]

    @provides(AuthenticationService)
    @inject(auth_config=AuthConfiguration)
    def provide_authentication_service(self, auth_config):
        # type: (AuthConfiguration)->AuthenticationService
        """
        Returns the used authentication service.

        :param auth_config: Injected. Auth configuration.
        :return: The authentication service.
        """

        if isinstance(auth_config.authentication_service_class, str):
            service_class = fetch_class(auth_config.authentication_service_class)
        else:
            service_class = auth_config.authentication_service_class

        @inject(service=service_class)
        def fetch_authentication_service(service):
            return service

        return fetch_authentication_service()
