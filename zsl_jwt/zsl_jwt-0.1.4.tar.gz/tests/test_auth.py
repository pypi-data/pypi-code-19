import json
from unittest.case import TestCase

from zsl.application.containers.container import IoCContainer
from zsl.application.modules.context_module import DefaultContextModule
from zsl.application.modules.logger_module import LoggerModule
from zsl.testing.zsl import ZslTestCase
from zsl.testing.zsl import ZslTestConfiguration

from zsl_jwt.auth.configuration import AuthConfiguration
from zsl_jwt.auth.controller import authenticate
from zsl_jwt.auth.module import AuthModule
from zsl_jwt.auth.service import AuthenticationService
from zsl_jwt.configuration import JWTConfiguration
from zsl_jwt.module import JWTModule


class TestAuthenticationService(AuthenticationService):
    def get_user_information(self, username):
        return ['role', None]

    def verify_password(self, username, password):
        return username == 'john' and password == 'doe'


class ZslAuthContainer(IoCContainer):
    logger = LoggerModule
    context = DefaultContextModule
    jwt_module = JWTModule
    auth_module = AuthModule()


class TestAuth(ZslTestCase, TestCase):
    ZSL_TEST_CONFIGURATION = ZslTestConfiguration(
        app_name='zsl_jwt_encode_test',
        container=ZslAuthContainer,
        config_object={
            JWTModule.JWT_CONFIG_NAME: JWTConfiguration('secret'),
            AuthModule.AUTH_CONFIG_NAME: AuthConfiguration(TestAuthenticationService)
        }
    )

    INVALID_CREDENTIALS_RESPONSE = {"code": "INVALID_CREDENTIALS",
                                    "message": "Username and password can not be verified."}

    def testAuthenticate(self):
        self.assertEqual(TestAuth.INVALID_CREDENTIALS_RESPONSE,
                         json.loads(authenticate('john', 'john')),
                         "Credentials john:john must be invalid")
        self.assertTrue('token' in authenticate('john', 'doe'),
                        'Credentials john:doe should be valid.')
