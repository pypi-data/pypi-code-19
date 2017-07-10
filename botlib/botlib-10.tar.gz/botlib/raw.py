# mad/raw.py
#
#

""" raw output using print. """

from .bot import Bot

class RAW(Bot):

    def say(self, channel, txt):
        print(txt)