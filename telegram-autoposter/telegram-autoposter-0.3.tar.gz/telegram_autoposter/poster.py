import logging

from telegram.ext import Updater


class Poster(object):
    def __init__(self, channel_id: str, updater: Updater):
        self.channel_id = channel_id
        self.bot = updater.bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def post(self, data, *args, **kwargs):
        self.logger.debug('Posting...')
        self.logger.debug('actually not')
