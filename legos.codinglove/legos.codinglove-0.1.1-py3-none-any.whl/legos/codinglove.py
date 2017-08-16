import requests

from Legobot.Lego import Lego
import logging

logger = logging.getLogger(__name__)


class CodingLove(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!codinglove'

    def handle(self, message):
        try:
            target = message['metadata']['source_channel']
            opts = {'target': target}
        except IndexError:
            logger.error('Could not identify message source in message: %s'
                         % str(message))
        base_url = 'http://thecodinglove.com/random'
        r = requests.get(base_url)
        if r.status_code == requests.codes.ok:
            self.reply(message, r.url, opts)
        else:
            self.reply(message, "I could not reach the page. Sorry.", opts)

    def get_name(self):
        return 'codinglove'

    def get_help(self):
        help_text = "Grab a random post from TheCodingLove" \
                    "Usage: !codinglove"
        return help_text
