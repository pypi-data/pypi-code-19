from abc import abstractmethod

from oe_utils.email.smtp import SMTPClient


class Notifier(object):

    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        self.email_client = SMTPClient(
            self.settings.get('daemon.email.smtp'),
            self.settings.get('daemon.email.sender')
        )

    @abstractmethod
    def notify(self, notifications_dict):
        """
        abstract method to notify by sending emails
        
        :param: notifications_dict: dictionary containing notification data

        """
        pass
