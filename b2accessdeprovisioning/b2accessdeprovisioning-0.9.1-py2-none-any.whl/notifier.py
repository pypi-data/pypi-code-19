from __future__ import absolute_import

import logging
import os
import smtplib

from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE

logger = logging.getLogger(__name__)

DEFAULT_USE_TLS = False


class MailNotifier():
    """Class for sending email notifications.
    """

    def __init__(self, **kwargs):
        """Consrtucts a new :class:`MailNotifier <MailNotifier>`.

        If specified, `host' is the name of the remote host to which to
        connect.  If specified, `port' specifies the port to which to connect.
        By default, the standard SMTP port (25) is used.

        :param host: (optional) SMTP host to connect to. If host is not
            specified, the local host is used.
        :param port: (optional) SMTP port to connect to. Defaults to the
            standard SMTP port (25).
        :param use_tls: (optional) whether to put the SMTP connection in TLS.
            Defaults to ``False``.
        :param user: (optional) login username if the SMTP server requires
            authentication.
        :param password: (optional) login password if the SMTP server requires
            authentication.
        """
        self.__host = kwargs.setdefault('host', '') 
        self.__port = kwargs.setdefault('port', 0) 
        self.__use_tls = kwargs.setdefault('use_tls', DEFAULT_USE_TLS)
        if 'user' in kwargs:
            self.__user = kwargs['user']
        if 'password' in kwargs:
            self.__password = kwargs['password']

    def send(self, send_from, send_to, subject, message, attachments=[]):
        """Sends the specified message.
        """
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Subject'] = subject

        body = MIMEText(message, 'plain')
        msg.attach(body)

        for attachment in attachments:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(attachment['message'])
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(attachment['filename']))
            msg.attach(part)

        s = smtplib.SMTP(self.__host, self.__port)
        s.ehlo()

        if self.__use_tls:
            s.starttls()
            # re-identify ourselves over TLS connection
            s.ehlo() 

        if self.__user or self.__password:
            s.login(self.__user, self.__password)

        s.sendmail(send_from, send_to, msg.as_string())

        s.quit()
