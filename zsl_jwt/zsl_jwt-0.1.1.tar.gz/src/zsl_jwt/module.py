"""
:mod:`zsl_jwt.module`
---------------------
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

from zsl_jwt.configuration import JWTConfiguration


class JWTModule(Module):
    """
    JWT module activation. Add to your IoCContainer to enable JWT support.

    It just provides the :class:`zsl_jwt.configuration.JWTConfiguration` so
    that the users may read the JWT configuration.
    """

    #: Variable name in config used for JWT configuration
    JWT_CONFIG_NAME = 'JWT'

    @provides(JWTConfiguration)
    @inject(config=Config)
    def provide_jwt_configuration(self, config):
        # type: (Config) -> JWTConfiguration
        """
        Returns the JWT configuration.

        :param config: Injected. Configuration object
        :return: Current JWT configuration.
        """
        return config.get(JWTModule.JWT_CONFIG_NAME)
