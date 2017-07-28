# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" fleet is a list of bots. """

from botlib.object import Object

class Fleet(Object):

    """ Fleet is a list of bots. """

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
        """ query bot in the fleet for a nick/origin match. Returns the origin. """
        for bot in self.bots:
            try:
                return bot._userhosts[nick]
            except (KeyError, AttributeError):
                pass

    def get_type(self, btype):
        """ return bot with botid in the fleet. """
        for bot in self.bots:
            if btype in bot._type:
                yield bot

    def partyline(self, txt):
        """ NEEDS IMPLEMENTING. """
        pass

    def remove(self, bot):
        """ remove a bot from fleet. """
        if bot in self.bots:
            self.bots.remove(bot)

    def say_id(self, id, channel, txt):
        """ echo text to channel on bot matching the given id. """
        bots = self.get_bot(id)
        for bot in bots:
            bot.say(channel, txt)
