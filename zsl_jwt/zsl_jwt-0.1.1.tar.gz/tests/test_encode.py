from datetime import timedelta
from unittest.case import TestCase

from zsl.application.containers.container import IoCContainer
from zsl.application.modules.context_module import DefaultContextModule
from zsl.application.modules.logger_module import LoggerModule
from zsl.testing.zsl import ZslTestCase
from zsl.testing.zsl import ZslTestConfiguration

from zsl_jwt.codec import ZslJwtExpiredSignatureError
from zsl_jwt.codec import ZslJwtInvalidAudienceError
from zsl_jwt.codec import ZslJwtInvalidNbfClaimError
from zsl_jwt.codec import decode
from zsl_jwt.codec import encode
from zsl_jwt.configuration import JWTConfiguration
from zsl_jwt.configuration import JWTProfile
from zsl_jwt.module import JWTModule


class ZslJwtContainer(IoCContainer):
    logger = LoggerModule
    context = DefaultContextModule
    jwt_module = JWTModule


class TestEncode(ZslTestCase, TestCase):
    SECRET = 'secret'
    PAYLOAD = {'a': 'b', 'c': {'d': 'e'}}
    ZSL_TEST_CONFIGURATION = ZslTestConfiguration(
        app_name='zsl_jwt_encode_test',
        container=ZslJwtContainer,
        config_object={
            JWTModule.JWT_CONFIG_NAME: JWTConfiguration(
                default_secret=SECRET,
                profiles={
                    'fail_nbf_claim': JWTProfile(
                        SECRET,
                        not_before=timedelta(seconds=30),
                        audience='fail_nbf_claim'
                    ),
                    'fail_exp_claim': JWTProfile(
                        SECRET,
                        expiration=timedelta(seconds=-30),
                        audience='fail_exp_claim'
                    ),
                    'correct': JWTProfile(
                        SECRET,
                        audience='correct'
                    ),
                }
            )
        }
    )

    def testEncodeDefaultProfile(self):
        token = encode(TestEncode.PAYLOAD)
        decoded_payload = decode(token)
        self.assertEqual(TestEncode.PAYLOAD, decoded_payload,
                         "The encoding/decoding process must result the "
                         "original payload.")

    def testEncodeInvalidAudienceClaim(self):
        token = encode(TestEncode.PAYLOAD)
        with self.assertRaises(ZslJwtInvalidAudienceError):
            decode(token, profile='correct')

    def testEncodeInvalidNotBeforeClaim(self):
        token = encode(TestEncode.PAYLOAD, profile='fail_nbf_claim')
        with self.assertRaises(ZslJwtInvalidNbfClaimError):
            decode(token, profile='fail_nbf_claim')

    def testEncodeExpiredSignatureClaim(self):
        token = encode(TestEncode.PAYLOAD, profile='fail_exp_claim')
        with self.assertRaises(ZslJwtExpiredSignatureError):
            decode(token, profile='fail_exp_claim')
