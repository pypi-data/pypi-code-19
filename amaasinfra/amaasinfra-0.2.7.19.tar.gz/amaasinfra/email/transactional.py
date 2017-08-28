"""
This module is used to manage transaction emails
"""
import boto3
import json
import requests
import pkg_resources
from amaasinfra.email.templates import EMAIL_TEMPLATES

class EmailClient(object):
    """
    This is a template class that all email clients should inherite from
    """
    def __init__(self):
        pass

    def send_mail(self, **kwargs):
        """
        This method should be implemented by every email client
        """
        raise NotImplementedError()


class SESClient(EmailClient):
    """
    This is an implementation of SES
    """
    def __init__(self, region='us-west-2'):
        self.client = boto3.client('ses', region_name=region)

    def send_mail(self, email, *args, **kwargs):
        """
        Implementation of SES sending email
        """
        if isinstance(email, SimpleEmail):
            message = email.message if not email.template else email.template

            if email.template and kwargs:
                for token, value in kwargs.items():
                    message = message.replace('{%s}' % token, value)

            return self.client.send_email(Source=email.sender,
                                          Destination={'ToAddresses': [email.to]},
                                          Message={'Subject': {'Data': email.subject,
                                                               'Charset': 'utf8'},
                                                   'Body': {'Text': {'Data': email.message,
                                                                     'Charset': 'utf8'},
                                                            'Html': {'Data': message,
                                                                     'Charset': 'utf8'}}},
                                          ReplyToAddresses=[email.sender])
        else:
            raise TypeError('Invalid parameter type, SimpleEmail object required.')


class SimpleEmail(object):
    def __init__(self, subject, message, to, sender='noreply@argomi.com', template_name=None):
        self._sender= sender
        self._to = to
        self._subject = subject
        self._message = message
        
        if template_name not in EMAIL_TEMPLATES:
            raise ValueError('Unknown template_name {}'.format(template_name))
        self._template = template_name

    @property
    def sender(self):
        return self._sender

    @property
    def to(self):
        return self._to

    @property
    def subject(self):
        return self._subject

    @property
    def message(self):
        return self._message

    @property
    def template(self):
        return EMAIL_TEMPLATES[self._template]

if __name__ == '__main__':
    SESClient().send_mail(SimpleEmail(subject='test email', message='test message', to='cheng.chen@amaas.com'))
  