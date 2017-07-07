from collections import namedtuple

Event = namedtuple('Event', ['identifier', 'action', 'arg', 'arg_is_client'])


def nick(identifier, nick):
    return Event(identifier, 'set_nick', nick, arg_is_client=False)


def connect(identifier, timestamp):
    return Event(identifier, 'connect', timestamp, arg_is_client=False)


def disconnect(identifier, timestamp):
    return Event(identifier, 'disconnect', timestamp, arg_is_client=False)


def kick(identifier, target_identifier):
    return Event(identifier, 'kick', target_identifier, arg_is_client=True)


def ban(identifier, target_identifier):
    return Event(identifier, 'ban', target_identifier, arg_is_client=True)
