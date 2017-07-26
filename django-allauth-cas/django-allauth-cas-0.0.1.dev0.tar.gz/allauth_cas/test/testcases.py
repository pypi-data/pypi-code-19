# -*- coding: utf-8 -*-
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.conf import settings
from django.test import TestCase as DjangoTestCase

import cas

from allauth_cas import CAS_PROVIDER_SESSION_KEY


class CASTestCase(DjangoTestCase):

    def patch_cas_response(
            self,
            valid_ticket,
            username=None, attributes={}):
        """
        Patch cas.CASClient in allauth_cas.views module with another CAS client
        selectable with label argument.

        Patch is stopped at the end of the current test.
        """
        if hasattr(self, '_patch_cas_client'):
            self.patch_cas_client_stop()

        class MockCASClient(cas.CASClientV2):
            _username = username

            def __init__(self_client, *args, **kwargs):
                kwargs.pop('version')
                super(MockCASClient, self_client).__init__(*args, **kwargs)

            def verify_ticket(self_client, ticket):
                if valid_ticket == '__all__' or ticket == valid_ticket:
                    username = self_client._username or 'username'
                    return username, attributes, None
                return None, {}, None

        self._patch_cas_client = patch(
            'allauth_cas.views.cas.CASClient',
            MockCASClient,
        )
        self._patch_cas_client.start()

    def patch_cas_client_stop(self):
        self._patch_cas_client.stop()
        del self._patch_cas_client

    def tearDown(self):
        if hasattr(self, '_patch_cas_client'):
            self.patch_cas_client_stop()


class CASViewTestCase(CASTestCase):

    def assertLoginSuccess(self, response, redirect_to=None):
        """
        Asserts response corresponds to a successful login.

        To check this, the response should redirect to redirect_to (default to
        /accounts/profile/, the default redirect after a successful login).
        Also CAS_PROVIDER_SESSION_KEY should be set in the client' session. By
        default, self.client is used.
        """
        if redirect_to is None:
            redirect_to = settings.LOGIN_REDIRECT_URL

        self.assertRedirects(
            response, redirect_to,
            fetch_redirect_response=False,
        )
        self.assertIn(
            CAS_PROVIDER_SESSION_KEY,
            response.wsgi_request.session,
        )

    def assertLoginFailure(self, response):
        """
        Asserts response corresponds to a failed login.
        """
        return self.assertInHTML(
            '<h1>Social Network Login Failure</h1>',
            str(response.content),
        )
