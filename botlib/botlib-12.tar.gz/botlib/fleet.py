# BOTLIB - Framework to program bots.
#
# Copyright (C) 2016,2017 by Bart Thate <bthate@dds.nl>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE 
# FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY 
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
        id = bot.id()
        if not self.get_bot(id):
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
        logging.info("! party %s" % txt)
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
