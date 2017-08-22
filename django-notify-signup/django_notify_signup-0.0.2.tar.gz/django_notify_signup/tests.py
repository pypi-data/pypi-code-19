from __future__ import absolute_import, unicode_literals

import mock

from django.contrib.auth import get_user_model
from django.test import TestCase


class NotifySignupTestCase(TestCase):

    @mock.patch('django_notify_signup.notify.mail_admins')
    def test_email_sent_on_user_signup(self, mock_mail_admins):
        get_user_model().objects.create_user('test', email='test', password='test')

        self.assertTrue(mock_mail_admins.called)
        self.assertIn(
            mock.call(u'User Signup', u'User signup: test'),
            mock_mail_admins.call_args_list
        )

    @mock.patch('django_notify_signup.notify.mail_admins')
    def test_disable_signup_notify_from_settings(self, mock_mail_admins):
        with self.settings(DISABLE_SIGNUP_NOTIFY=True):
            get_user_model().objects.create_user('test', email='test', password='test')

            self.assertFalse(mock_mail_admins.called)
