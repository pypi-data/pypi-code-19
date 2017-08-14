# BOTLIB Framework to program bots
#
# botlib/users.py
#
# Copyright 2017 B.H.J Thate
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" class to access user records. """

from .db import Db
from .object import Object
from .utils import userhost

import logging

class User(Object):

    """ User object to store user data. """ 

    pass

class Users(Db):

    """ Users class providing methods to check/verify/allow users based on origin. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._userhosts = Object()

    def add(self, origin, perms):
        """ add a user to the store. """
        from .space import cfg
        user = self.fetch(origin)
        if not user:
            user = User()
            user.user = userhost(origin)
            user.perms = [x.upper() for x in perms]
            user.save()
        else:
            user.user = userhost(origin)
            user.perms = [x.upper() for x in perms]
            user.save()
        logging.warn("# user %s" % user)
        return user

    def allowed(self, origin, perm):
        """ check whether a user has a permission. """ 
        from .space import cfg, fleet
        if origin == cfg.owner:
            return True
        perm = perm.upper()
        user = self.fetch(origin)
        if user and perm in user.perms:
            return True
        logging.warn("# denied %s %s" % (origin, perm))
        return False

    def delete(self, origin, perms):
        """ add a user to the store. """
        user = self.fetch(origin)
        if user:
            user.perms.remove(perms)
            user.sync()
        return user

    def fetch(self, origin):
        """ return user data. """
        o = userhost(origin)
        return self.last("user", o)

    def set(self, origin, perms):
        """ set a permission of a user. """
        user = self.fetch(origin)
        if user:
           if perms.upper() not in user.perms:
               user.perms.append(perms.upper())
               user.sync()
        return user
