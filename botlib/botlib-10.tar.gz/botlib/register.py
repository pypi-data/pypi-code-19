# mad/register.py
#
#

""" Object with list for multiple values. """

from botlib.object import Object

import logging

class Register(Object):

    def register(self, key, val, force=True):
        if key not in self:
            self[key] = []
        if val not in self.get(key, []):
            self[key].append(val)
        
    def find(self, txt=None):
        for key, value in self.items():
            if txt and txt in key:
                yield value
            else:
                yield value
