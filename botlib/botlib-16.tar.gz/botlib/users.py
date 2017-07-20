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
