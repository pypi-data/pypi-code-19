import argparse
import random
import string
from datetime import datetime

from helga.db import db
from helga.plugins import command, match, random_ack, ResponseNotReady


HELP_TEXT = """Team plugin to track candidates and interview process.
Refer to https://github.com/narfman0/helga-team#usage for more info."""


def handle_add(client, channel, parser, nick):
    set_args = parser_to_dict(parser)
    # generate some defaults
    if 'id' not in set_args:
        set_args['id'] = generate_id()
    if 'status' not in set_args:
        set_args['status'] = 'pending'
    set_args['last_update'] = str(datetime.now())
    db.team.candidates.insert(set_args)
    return random_ack()


def handle_update(client, channel, parser, nick):
    get_args = {}
    # if id is passed, use id. name is a fallback.
    if parser.id:
        get_args['id'] = parser.id
    elif parser.name:
        get_args['name'] = parser.name
    set_args = parser_to_dict(parser)
    set_args['last_update'] = str(datetime.now())
    db.team.candidates.find_one_and_update(
        get_args, {'$set': set_args}
    )
    return random_ack()


def handle_status(client, channel, parser, nick):
    get_args = parser_to_dict(parser)
    candidates = db.team.candidates.find(get_args)
    for candidate in candidates:
        client.msg(channel, status(candidate))


def handle_remove(client, channel, parser, nick):
    get_args = parser_to_dict(parser)
    db.team.candidates.remove(get_args)
    return random_ack()


def logic(client, channel, command, parser, nick):
    if command == 'add':
        return handle_add(client, channel, parser, nick)
    elif command == 'update':
        return handle_update(client, channel, parser, nick)
    elif command == 'status':
        handle_status(client, channel, parser, nick)
        raise ResponseNotReady
    elif command == 'remove' or command == 'delete':
        return handle_remove(client, channel, parser, nick)
    return 'Team command unknown: ' + command


@command('team', help=HELP_TEXT, shlex=True)
def team(client, channel, nick, message, cmd, args):
    return logic(client, channel, args[0], parse(args[1:]), nick)


def parse(args):
    """ Parse arguments given to command """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id')
    parser.add_argument('-n', '--name')
    parser.add_argument('-s', '--status')
    parser.add_argument('-o', '--owner')
    parser.add_argument('-r', '--recruiter')
    parser.add_argument('-c', '--code_review')
    return parser.parse_args(args)


def status(candidate):
    """ Print status msg about a particular candidate """
    response = candidate['name'] or "No name given"
    if 'owner' in candidate:
        response += ', owner: ' + candidate['owner']
    if 'recruiter' in candidate:
        response += ', recruiter: ' + candidate['recruiter']
    if 'status' in candidate:
        response += ', status: ' + candidate['status']
    if 'code_review' in candidate:
        response += ', code_review: ' + candidate['code_review']
    return response + ', id: ' + candidate['id']


def parser_to_dict(parser):
    """ Given a parser, generate mongo args """
    args = {}
    if parser.id:
        args['id'] = parser.id
    if parser.name:
        args['name'] = parser.name
    if parser.status:
        args['status'] = parser.status
    if parser.owner:
        args['owner'] = parser.owner
    if parser.recruiter:
        args['recruiter'] = parser.recruiter
    if parser.code_review:
        args['code_review'] = parser.code_review
    return args


def generate_id(n=6):
    """ Create a random id. Why not. """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
