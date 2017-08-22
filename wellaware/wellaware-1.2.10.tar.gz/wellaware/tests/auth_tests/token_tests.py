from __future__ import unicode_literals

from wellaware.client import Token, Tokens
from wellaware.tests.base import *


class TokenTests(BaseClientTestCase):

    @attr('unit', 'tokens')
    @responses.activate
    def test_login(self):
        resp = {'token': WA_ADMIN_TOKEN }
        responses.add(responses.POST, 'http://localhost/tokens', json=resp, status=200)

        token = Tokens.login("admin@wellaware.us", "test")
        self.assertIsInstance(token, Token)
        self.assertTrue(len(token.jwt) > 0)
        self.assertEquals('jzQrLHA50XTh18zwbTg6hRvYSWgBv40K', token.audience)
        self.assertEquals('https://wellaware.auth0.com/', token.issuer)
        self.assertEquals(1489174893, token.created)
        self.assertEquals(1489616119, token.expiration)
        self.assertEquals('admin@wellaware.us', token.username)
        self.assertEquals('admin@wellaware.us', token.email)
        self.assertEquals('Admin', token.given_name)
        self.assertEquals('WellAware', token.family_name)
        self.assertEquals('America/Chicago', token.timezone)
        self.assertEquals(149480004, token.tenant_id)
        self.assertEquals('WellAware', token.tenant_name)
        self.assertEquals('04b7bdd2-219c-437e-a113-c2253425134a', token.tenant_uuid)
        self.assertEquals('auth0|1234567890', token.subject)
        self.assertEquals(2482924076, token.subject_id)
        self.assertEquals(None, token.impersonation)
        self.assertEquals(None, token.legacy_token)
        self.assertListEqual(
            ['User', 'WellAware-Service', 'WellAware-Admin', 'WellAware-Serivce', 'Admin', 'Controller'],
            token.roles
        )
        self.assertListEqual(
            ['*:*:*', 'tokens', 'reverseLookup:retrieve', 'impersonate:*', '*:retrieve:*'],
            token.permissions
        )