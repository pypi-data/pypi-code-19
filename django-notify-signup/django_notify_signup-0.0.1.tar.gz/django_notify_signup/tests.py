from __future__ import absolute_import, unicode_literals

import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


class NotifySignupTestCase(TestCase):

    @mock.patch('django_notify_signup.notify.mail_admins')
    def test_email_sent_on_user_signup(self, mock_mail_admins):
        get_user_model().objects.create_user('test', email='test', password='test')

        self.assertTrue(mock_mail_admins.called)
