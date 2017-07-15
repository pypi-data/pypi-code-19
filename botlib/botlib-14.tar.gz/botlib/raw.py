# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" raw output using print. """

from .bot import Bot

class RAW(Bot):

    def say(self, channel, txt):
        from .space import cfg
        if self.verbose or cfg.verbose:
            print(txt)
