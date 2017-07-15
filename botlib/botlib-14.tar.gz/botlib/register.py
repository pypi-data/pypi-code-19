# BOTLIB - Framework to program bots
#
# 14-7-2017 removed copyright

""" object with list for multiple values. """

from .object import Object
from .utils import sname

import logging

class Register(Object):

    def register(self, key, val, force=False):
        if key not in self:
            self[key] = []
        if not force and val in self.get(key, []):
            return
        self[key].append(val)
        
    def find(self, txt=None):
        for key, value in self.items():
            if txt and txt in key:
                yield value
            else:
                yield value
