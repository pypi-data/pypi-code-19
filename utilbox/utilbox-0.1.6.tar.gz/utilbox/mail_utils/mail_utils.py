"""
Utility module to handle sending of email messages.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class MailUtils:
    """
    Utility class containing methods for sending of email messages.
    """

    def __init__(self, smtp_server, sender_email_id):
        self.smtp_server = smtp_server
        self.sender_email_id = sender_email_id

    def send_mail_plain(self, recipient_email_id, email_subject, reply_to_email, message_string):
        """
        Sends a plain-text email message.

        :param recipient_email_id: The email ID of the recipient.
        :param email_subject: The subject of the email.
        :param reply_to_email: The 'reply-to' email address
        :param message_string: The body of the email message.

        :return: True, if message was sent successfully, False otherwise.
        :rtype: bool
        """

        # Create message container - the correct MIME type is multipart/alternative.
        email_message = MIMEText(message_string)

        email_message['Subject'] = email_subject
        email_message['From'] = self.sender_email_id
        email_message['To'] = reply_to_email

        try:
            # Send the message via local SMTP server.
            smtp_session = smtplib.SMTP(self.smtp_server)

            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            smtp_session.sendmail(self.sender_email_id, recipient_email_id, email_message.as_string())

            smtp_session.quit()

            return True
        except Exception as ex:
            import traceback
            traceback.format_exc()

        return False

    @staticmethod
    def _create_html_message(plain_message_string):
        """
        Internal method to convert plain-text message string to HTML.

        :param plain_message_string: The message string to converted to HTML.

        :return: The HTML-based message string.
        :rtype: str
        """

        return "<html><head></head><body><p>" + str(plain_message_string) + "</p></body></html>"

    def send_mail_html(self, recipient_email_id, email_subject, reply_to_email, message_string):
        """
        Sends an HTML-format email message.

        :param recipient_email_id: The email ID of the recipient.
        :param email_subject: The subject of the email.
        :param reply_to_email: The 'reply-to' email address
        :param message_string: The body of the email message.

        :return: True, if message was sent successfully, False otherwise.
        :rtype: bool
        """

        # Create message container - the correct MIME type is multipart/alternative.
        email_message = MIMEMultipart('alternative')

        email_message['Subject'] = email_subject
        email_message['From'] = self.sender_email_id
        email_message['To'] = reply_to_email

        # Create the body of the message (a plain-text and an HTML version).
        text = message_string
        html = self._create_html_message(message_string)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        email_message.attach(part1)
        email_message.attach(part2)

        try:
            # Send the message via local SMTP server.
            smtp_session = smtplib.SMTP(self.smtp_server)

            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            smtp_session.sendmail(self.sender_email_id, recipient_email_id, email_message.as_string())

            smtp_session.quit()

            return True
        except Exception as ex:
            import traceback
            traceback.format_exc()

        return False
