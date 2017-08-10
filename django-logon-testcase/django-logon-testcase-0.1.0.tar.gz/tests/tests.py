#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-logon-testcase
------------

Tests for `django-logon-testcase` models module.
"""

from django.test import TestCase

from logon_testcase import LogonMixin


class TestLogonTestCaseTest(LogonMixin, TestCase):
    def test_is_logged_on(self):
        self.assertEquals(
            str(self.client.session.get('_auth_user_id')),
            str(self.user.pk),
        )

    def test_logout(self):
        self.client.logout()
