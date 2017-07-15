# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" fleet is a list of bots. """

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
                yield bot

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
        logging.info("! party %s" % txt)
        for bot in self.bots:
            try:
                bot._socket.write(txt)
            except AttributeError:
                continue
            except:
                logging.error(get_exception())

    def remove(self, bot):
        if bot in self.bots:
            self.bots.remove(bot)
        
    def say_id(self, id, channel, txt):
        bots = self.get_bot(id)
        if bots:
            for bot in bots:
                bot.say(channel, txt)
