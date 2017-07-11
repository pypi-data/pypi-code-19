# botlib/fleet.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

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
            logging.info("! add %s" % bot.id())
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
