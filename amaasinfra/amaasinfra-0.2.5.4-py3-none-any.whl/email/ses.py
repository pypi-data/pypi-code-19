"""
This module is used to manage transaction emails
"""
import boto3
import json
import requests


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
    def __init__(self):
        super(EmailClient, self).__init__()
        self.client = boto3.client('ses', region_name='us-west-2')

    def send_mail(self, **kwargs):
        """
        Implementation of SES sending email
        """
        return self.client.send_email(
            Source=kwargs.get('sender', ''),
            Destination={'ToAddresses': [kwargs.get('to', '')]},
            Message={'Subject': {'Data': kwargs.get('subject', ''),
                                 'Charset': 'utf8'},
                     'Body': {'Text': {'Data': kwargs.get('message', ''),
                                       'Charset': 'utf8'},
                              'Html': {'Data': kwargs.get('message', ''),
                                       'Charset': 'utf8'}}},
            ReplyToAddresses=[kwargs.get('reply_to', 'noreply@amaas.com')])
