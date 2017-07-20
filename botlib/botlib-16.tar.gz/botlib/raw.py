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

""" raw output using print. """

from .bot import Bot

class RAW(Bot):

    """ Bot that outputs to stdout, using self.verbose or cfg.verbose (-v option) to determine whether to output or not. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose = False

    def say(self, channel, txt):
        """ output txt to stdout. """
        from .space import cfg
        if self.verbose or cfg.verbose:
            print(txt)
