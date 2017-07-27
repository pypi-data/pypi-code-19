# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

from django.conf import settings

from .mail_hook import MailBackendHook
from django.core.exceptions import ImproperlyConfigured


class AddBccEmailBackend(MailBackendHook):
    def __init__(self, *args, **kwarg):
        super(AddBccEmailBackend, self).__init__(*args, **kwarg)
        bcc_list = getattr(settings, 'EMAIL_BCC')
        if bcc_list is None:  # pragma: no cover
            raise ImproperlyConfigured('EMAIL_BCC must be set')
        self.__bcc_list = bcc_list

    def send_messages(self, email_messages):
        for email_message in email_messages:
            s = set(self.__bcc_list)
            s.update(email_message.bcc)
            email_message.bcc = list(s)
        return self.__dict__['_upper_'].send_messages(email_messages)
