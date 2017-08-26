# coding=utf-8
from __future__ import absolute_import, unicode_literals

import os

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase, override_settings

from ..forms import ContactForm


@override_settings(
    TEMPLATE_DIRS=(os.path.join(os.path.dirname(__file__), 'templates'),))
class ContactFormViewTests(TestCase):

    def test_get(self):
        """
        HTTP GET on the form view just shows the form.

        """
        contact_url = reverse('contact_form:contact_form')

        response = self.client.get(contact_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response,
                                'contact_form/contact_form.html')

    def test_send(self):
        """
        Valid data through the view results in a successful send.

        """
        contact_url = reverse('contact_form:contact_form')
        data = {'name': 'Test',
                'email': 'test@example.com',
                'body': 'Test message'}

        response = self.client.post(contact_url,
                                    data=data)

        self.assertRedirects(response,
                             reverse('contact_form:contact_form_sent'))

        self.assertEqual(1, len(mail.outbox))

        message = mail.outbox[0]
        self.assertTrue(data['body'] in message.body)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL,
                         message.from_email)
        form = ContactForm(request=RequestFactory().request)
        self.assertEqual(form.recipient_list,
                         message.recipients())

    def test_invalid(self):
        """
        Invalid data doesn't work.

        """
        contact_url = reverse('contact_form:contact_form')
        data = {'name': 'Test',
                'body': 'Test message'}

        response = self.client.post(contact_url,
                                    data=data, **{'Accept-Language': 'en-us'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(mail.outbox))
