import argparse as ap
import logging
import os
import sys

from pymygdala import (LogDumper, LogHandler, SendEvent, SendNRAOEvent, version)

_ERR_MISSING_PROFILE = r"""ERROR: {script} can't deduce the 'profile', give it the --profile argument or set the CAPO_PROFILE environment variable! Geeze!

"""
_ERR_UNKNOWN_LEVEL = r"""ERROR: {script} pass unknown logging level {level}, expected DEBUG, INFO, WARN or ERROR
"""

_DUMPLOGS_NAME = 'pym-dumplogs'
_DUMPLOGS_DESCRIPTION = r"""{script}, {version}: connect to a RabbitMQ server and dump the logs out.
"""
_DUMPLOGS_EPILOG = r"""Return values:
   0: everything worked as expected
   1: missing CAPO profile, no --profile argument or environment variable
   2: can't connect to specified RabbitMQ server
"""


def get_common_parser(description, epilog):
    r""" Returns a parser for all these scripts with all the common parameters.

    :param description:
    :param epilog:
    :return:
    """
    p = ap.ArgumentParser(description=description, epilog=epilog,
                          formatter_class=ap.RawDescriptionHelpFormatter)
    p.add_argument('--profile', action='store',
                   help='CAPO profile name to use, e.g. test, production')
    p.add_argument('--exchange', action='store',
                   help='exchange name to use, e.g. archive.logs')
    p.add_argument('--type', action='store', dest='exchange_type',
                   help='exchange type to use, e.g. fanout')
    p.add_argument('--hostname', action='store',
                   help='server name of the RabbitMQ server')
    p.add_argument('--username', action='store',
                   help='username of the RabbitMQ server')
    p.add_argument('--password', action='store',
                   help='password of the RabbitMQ server')
    p.add_argument('--port', action='store', type=int,
                   help='port number of the RabbitMQ server')
    p.add_argument('--key', action='store', dest='routing_key',
                   help='routing key, e.g. archive.logs')
    return p


def ns_to_d(ns):
    r""" Convert a namespace into a dict, dropping properties that are 'None' along the way.

    :param ns:
    :return:
    """
    return {key: value for key, value in vars(ns).items() if value is not None}


def get_settings(parser, script):
    r""" Get the settings from a given parser, for a given script.

    :param parser:
    :param script:
    :return:
    """
    d = ns_to_d(parser.parse_args())

    if 'profile' not in d and 'CAPO_PROFILE' not in os.environ:
        sys.stderr.write(_ERR_MISSING_PROFILE.format(script=script))
        parser.print_help()
        sys.exit(1)
    d['profile'] = os.environ['CAPO_PROFILE'] if 'profile' not in d else d['profile']
    return d


def get_dumplogs_parser():
    r""" Get a parser for the pym-dumplogs CLI.

    :return:
    """
    p = get_common_parser(_DUMPLOGS_DESCRIPTION.format(script=_DUMPLOGS_NAME, version=version),
                          _DUMPLOGS_EPILOG)
    p.add_argument('--outfile', action='store', default='-',
                   help='write output to file, - for STDOUT')
    return p


def dumplogs():
    r""" The pym-dumplogs CLI.

    :return:
    """
    parser = get_dumplogs_parser()
    settings = get_settings(parser, _DUMPLOGS_NAME)
    dumper = LogDumper(**settings)
    dumper.dump()


_SENDLOG_NAME = 'pym-sendlog'
_SENDLOG_DESCRIPTION = r"""{script}, {version}: a command line tool for logging to RabbitMQ."""
_SENDLOG_EPILOG = r"""Return values:
   0: everything worked as expected
   1: missing CAPO profile, no '--profile' argument or environment variable
   2: can't connect to specified RabbitMQ server
   3: unknown logging level, should be DEBUG, INFO, WARN or ERROR
"""


def get_sendlog_parser():
    p = get_common_parser(_SENDLOG_DESCRIPTION.format(script=_SENDLOG_NAME, version=version),
                          _SENDLOG_EPILOG)
    r = p.add_argument_group('Required Arguments')
    r.add_argument('--level', action='store', required=True,
                   help='logging level, e.g. DEBUG, WARN')
    r.add_argument('--message', action='store', required=True,
                   help='message to log')
    r.add_argument('--app', dest='application', action='store', required=True,
                   help='the application name to log as')
    return p


def sendlog():
    r""" The pym-sendlog CLI.

    :Returns:
         0: everything worked as expected
         1: can't deduce CAPO_PROFILE
         2: error talking to RabbitMQ
         3: bad level (not DEBUG, INFO, WARN or ERROR)
    """
    parser = get_sendlog_parser()
    settings = get_settings(parser, _SENDLOG_NAME)
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    handler = LogHandler(**settings)
    log.addHandler(handler)
    fn = None
    if settings['level'] == 'DEBUG':
        fn = log.debug
    elif settings['level'] == 'INFO':
        fn = log.debug
    elif settings['level'] == 'WARN':
        fn = log.debug
    elif settings['level'] == 'ERROR':
        fn = log.debug

    if fn is not None:
        try:
            fn(settings['message'])
        except:
            sys.stderr.write(_ERR_MISSING_PROFILE.format(script=_SENDLOG_NAME))
            parser.print_help()
            sys.exit(2)
    else:
        sys.stderr.write(_ERR_UNKNOWN_LEVEL.format(script=_SENDLOG_NAME, level=settings['level']))
        parser.print_help()
        sys.exit(4)


_SENDEVENT_NAME = 'pym-sendevent'
_SENDEVENT_DESCRIPTION = r"""{script}, {version}: send an event to a RabbitMQ server."""
_SENDEVENT_EPILOG = r"""Return values:
   0: everything worked as expected
   1: missing CAPO profile, no '--profile' argument or environment variable
   2: can't connect to specified RabbitMQ server
"""


def get_sendevent_parser():
    p = get_common_parser(_SENDEVENT_DESCRIPTION.format(script=_SENDEVENT_NAME, version=version),
                          _SENDEVENT_EPILOG)
    p.add_argument('--event', dest='eventName', action='store',
                   help='eventName to send, e.g. runSdmIngestionWorkflow')
    p.add_argument('--nrao', dest='nrao_event', action='store_true', default=False,
                   help='add NRAO specific fields to the event')
    p.add_argument('--message', action='append', default=[],
                   help='provide a KEY=VALUE pair in the event message, can be used multiple times')
    p.add_argument('--md-name', dest='md_name', action='store', default='logData',
                   help='name of an extra metadata message section')
    p.add_argument('--metadata', action='append', default=[],
                   help="provide a KEY=VALUE pair in the md-name section of the message; can be used multiple times")
    r = p.add_argument_group('Required Arguments')
    r.add_argument('--app', dest='application', action='store', required=True,
                   help='the application name to log as')
    return p


def build_event(settings):
    result = dict(arg.split('=') for arg in settings['message'])
    if 'md_name' in settings:
        result[settings['md_name']] = dict(arg.split('=') for arg in settings['metadata'])
    if 'eventName' in settings:
        result['eventName'] = settings['eventName']
    return result


def sendevent():
    r""" The pym-sendevent CLI.

    :Returns:
         0: everything worked as expected
         1: can't deduce CAPO_PROFILE
         2: error talking to RabbitMQ
    """
    parser = get_sendevent_parser()
    settings = get_settings(parser, _SENDEVENT_NAME)
    event = build_event(settings)
    try:
        if settings['nrao_event']:
            se = SendNRAOEvent(**settings)
        else:
            se = SendEvent(**settings)
        se.send(event)
    except:
        sys.stderr.write(_ERR_MISSING_PROFILE.format(script=_SENDEVENT_NAME))
        parser.print_help()
        sys.exit(2)
