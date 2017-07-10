# mad/fleet.py
#
#

from botlib.object import Object

import logging

class Fleet(Object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bots = []

    def __iter__(self):
        for bot in self.bots:
            yield bot

    def add(self, bot):
        """ insert a bot into a fleet. """
        id = bot.id()
        if not self.get_bot(id):
            logging.info("# add %s" % bot.id())
            self.bots.append(bot)

    def echo(self, id, txt):
        """ echo txt to a specific bot. """
        for bot in self.bots:
            if bot.id() == id:
                bot.raw(txt)

    def get_bot(self, id):
        """ return bot with botid in the fleet. """
        for bot in self.bots:
            if id in bot.id():
                return bot

    def get_origin(self, nick):
        for bot in self.bots:
            try:
                return bot._userhosts[nick]
            except (KeyError, AttributeError):
                pass

    def get_type(self, type):
        """ return bot with botid in the fleet. """
        for bot in self.bots:
            if type in bot._type:
                yield bot

    def partyline(self, txt):
        logging.warn("# party %s" % txt)
        for bot in self.bots:
            try:
                bot._socket.write(txt)
            except AttributeError:
                continue
            except:
                logging.error(get_exception())

    def say_id(self, id, channel, txt):
        bot = self.get_bot(id)
        if bot:
            bot.say(channel, txt)
