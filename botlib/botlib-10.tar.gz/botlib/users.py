# mad/users.py
#
#

""" class to access user records. """

from .db import Db
from .object import Object, slice
from .utils import userhost

import logging

class Users(Db):

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
        logging.warn("denied %s %s" % (origin, perm))
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

class User(Object):

    pass

def meet(event):
    """ create an user record. """
    from .space import fleet, users
    if not users.allowed(event.origin, "OPER"):
        event.reply("you are not allowed to give the meet command.")
        return
    perms = ["USER", ]
    try: 
        nick, *permissions = event._parsed.args
        perms.extend(permissions)
    except:
        event.reply("meet <nick> [<perm1> <perm2>]")
        return
    origin = fleet.get_origin(nick)
    if not origin:
        origin = nick
    user = users.add(origin, perms)
    if user:
        event.reply("user %s created" % origin)
    else:
        event.reply("missing userhost for %s" % origin)

def perm(event):
    """ add/change permissions of an user. """
    from .space import fleet, users
    if not users.allowed(event.origin, "OPER"):
        event.reply("you are not allowed to give the perm command.")
        return
    try:
        nick, perms = event._parsed.args
    except:
        event.reply("perm <origin> <perm>")
        return
    origin = fleet.get_origin(nick)
    user = users.set(origin, perms)
    if not user:
        event.reply("can't find a user matching %s" % origin)
        return
    event.reply(slice(user, skip=["type"]))

def delperm(event):
    """ delete permissions of an user. """
    from .space import fleet, users
    if not users.allowed(event.origin, "OPER"):
        event.reply("you are not allowed to give the delperm command.")
        return
    try:
        nick, perms = event._parsed.args
    except:
        event.reply("perm <origin> <perm>")
        return
    origin = fleet.get_origin(nick)
    try:
        user = users.delete(origin, perms)
    except Exception as ex:
        event.reply(str(ex))
        return
    if not user:
        event.reply("can't find a user matching %s" % origin)
        return
    event.reply(slice(user, skip=["type"]))

def user(event):
    """ show user selected by userhost. """
    from .space import fleet, users
    if not event._parsed.rest:
        event.reply("user <origin>")
        return
    nick = event._parsed.args[0]
    origin = fleet.get_origin(nick)
    u = users.fetch(origin)
    if u:
        event.reply(slice(u, skip=["type"]))

def w(event):
    """ show user data. """
    from .space import users
    u = users.fetch(event.userhost) 
    if u:
        event.reply(u)
    else:
        event.reply("no matching user found.")
