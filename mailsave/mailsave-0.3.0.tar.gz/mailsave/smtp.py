import logging

from mailsave import save
from smtpd import SMTPServer


class MailSaveServer(SMTPServer):
    def __init__(self, host, port, dir):
        logging.basicConfig(level=logging.INFO)
        super().__init__((host, port), None)
        self.dir = dir
        logging.info('Listening for mail on {}:{}'.format(host, port))

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        logging.info('Received mail from address {} from peer {}'.format(mailfrom, peer))
        save(data)
