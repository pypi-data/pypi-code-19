from django.test import TestCase, override_settings
from maas.exceptions import *
from maas.models import *
import responses
import re


class MailgunV3Test(TestCase):

    def setUp(self):
        def buildMail():
            return Mail(sender='test@test.com', recipient='test@test.com', subject='subject', body='body')

        self.buildMail = buildMail

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3'})
    def test_no_domain(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test'})
    def test_no_api_key(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_invalid_api_key(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=401)

        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_invalid_domain(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=404)

        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_mailgun_error(self):
        for status in [500, 502, 503, 504]:
            responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=status)

            with self.assertRaises(MaasProviderException):
                mail = self.buildMail()
                mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_bad_request(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=400)

        with self.assertRaises(MaasUnknownException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_bad_request(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=407)

        with self.assertRaises(MaasUnknownException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_bad_request(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=402)

        with self.assertRaises(MaasUnknownException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_successful_delivery(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=200)
        mail = self.buildMail()
        mail.save()
        self.assertEqual(mail.delivered, False)
        mail.send()
        mail = Mail.objects.get(id=mail.id)
        self.assertEqual(mail.delivered, True)