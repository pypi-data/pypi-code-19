#!/usr/bin/env python
import pprint
import logging
from collections import namedtuple

from requests.exceptions import ConnectionError
from client.exceptions import FaaspotException

from .table import print_data
from .commands.command import commands
from .cli.arguments import parser, root_parsers

# logging options
# https://docs.python.org/3/library/logging.html
# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)-8s] %(message)s', datefmt="%H:%M:%S")
ch.setFormatter(formatter)
logger = logging.getLogger(__name__)


def set_logging_level(vrbose_level):
    external_loggers = ['requests', 'fas.client.httpclient']
    internal_loggers = ['fas', '__main__', 'commands', 'client', 'utils']
    internal_loggers_level = logging.INFO
    external_loggers_level = logging.WARNING
    if vrbose_level >= 1:
        internal_loggers_level = logging.DEBUG
    if vrbose_level >= 2:
        external_loggers_level = logging.INFO
    if vrbose_level >= 3:
        external_loggers_level = logging.DEBUG
    for logger_name in internal_loggers:
        i_logger = logging.getLogger(logger_name)
        i_logger.setLevel(internal_loggers_level)
        i_logger.addHandler(ch)
    for logger_name in external_loggers:
        i_logger = logging.getLogger(logger_name)
        i_logger.setLevel(external_loggers_level)
        i_logger.addHandler(ch)


def main():
    args = parser.parse_args()
    input = dict(args._get_kwargs())

    selected_root_arg = [(root, input.get(root))
                         for root in root_parsers if input.get(root)][0]
    RootArg = namedtuple('RootArg', ['root', 'action'], verbose=False)
    root_arg = RootArg(*selected_root_arg)

    # handle the verbose input, and delete it.
    # it's not relevant for the fas commands..
    set_logging_level(args.verbose)
    del input[root_arg.root]
    del input['verbose']

    command = commands.get(root_arg.root)
    try:
        command_instance = command(root_arg.action, **input)
        result = command_instance.run_function()
        if command_instance.columns:
            print_data(command_instance.columns, result, '{0}:'.format(command_instance.name))
        elif any(isinstance(result, formatted_type) for formatted_type in [dict, list]):
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)
        else:
            print result
    except ConnectionError as ex:
        error_message = 'Failed to connect to FaaSpot server. \n' \
                        'Please verify connection parameters. \n' \
                        'Exception: {0}'.format(ex)
        print error_message
    except FaaspotException as ex:
        error_message = 'Failed to run command. \n' \
                        'Exception: {0}'.format(ex)
        print error_message
    except Exception as ex:
        print 'Failed. {0}'.format(ex)
        # error_message = 'Failed to run command. Exception: {0}'.format(ex)
        # print error_message


if __name__ == '__main__':
    main()
