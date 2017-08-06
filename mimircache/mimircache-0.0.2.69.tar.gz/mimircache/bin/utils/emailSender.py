# coding=utf-8
"""
this module sends out email alert 
"""

import os, sys, time
import smtplib


class email_const:
    smtp_server_163 = "smtp.163.com"
    smtp_port_163 = 465

    smtp_server_gmail = "smtp.gmail.com"
    smtp_port_gmail = 587

    message_template = "From: From Jason <{sender}>\r\n" \
                       "To: To Juncheng <{receiver}>\r\n" \
                       "MIME-Version: 1.0\r\n" \
                       "Content-type: text/html\r\n" \
                       "Subject: {topic}\r\n\r\n{message}"


class EmailClient:
    def __init__(self, smtp_server,
                 login_username, login_password,
                 smtp_port=25, SSL=False, TLS=False):

        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login_username = login_username
        self.login_password = login_password

        self.SSL = SSL
        self.TLS = TLS
        if SSL:
            self.email_server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            self.email_server = smtplib.SMTP(smtp_server, smtp_port)

        if TLS:
            self.email_server.starttls()

        try:
            # server.ehlo()
            # server.starttls()
            self.email_server.login(login_username, login_password)
        except Exception as e:
            print(e, file=sys.stderr)
            exit(1)

    def send_email(self, receiver, message, topic="No topic"):

        try:
            if False:
                print("send " + email_const.message_template.format(sender=self.login_username
                                                                    , receiver=receiver
                                                                    , topic=topic
                                                                    , message=message))

            self.email_server.sendmail(self.login_username, receiver,
                                       email_const.message_template.format(sender=self.login_username
                                                                           , receiver=receiver
                                                                           , topic=topic
                                                                           , message=message))

        except Exception as e:
            print("ERROR: {}".format(e), file=sys.stderr)
            exit(1)

    def close(self):
        self.email_server.quit()


class DefaultEmailClient(EmailClient):
    def __init__(self):
        super(DefaultEmailClient, self).__init__(email_const.smtp_server_gmail,
                         "jasonEmailSender0517@gmail.com",
                         "YJC1a1a11a",
                         smtp_port=email_const.smtp_port_gmail,
                         SSL=False,
                         TLS=True)


if __name__ == "__main__":
    client = EmailClient(email_const.smtp_server_gmail
                         , "jasonemailsender0517@gmail.com", "YJC1a1a11a"
                         , smtp_port=email_const.smtp_port_gmail
                         , SSL=False
                         , TLS=True)
    client.send_email("peter.waynechina@gmail.com", "test")
    client.close()





