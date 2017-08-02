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

""" object with list for multiple values. """

from .object import Object

class Register(Object):

    """ class to register key,value pairs. """

    def register(self, key, val, force=False):
        """ register value with key, using force argumentto determine to overwrite or not. """
        if key not in self:
            self[key] = []
        if not force and val in self.get(key, []):
            return
        self[key].append(val)

    def find(self, txt=None):
        """ search a register object for keys matching txt. """
        for key, value in self.items():
            if txt and txt in key:
                yield value
            else:
                yield value
