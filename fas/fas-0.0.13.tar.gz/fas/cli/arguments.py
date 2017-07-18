#!/usr/bin/env python
import argparse

from spots import add_spots_args
from deployments import add_deployments_args
from executions import add_executions_args
from profiles import add_profiles_args


def add_verbose_to_all_commands(parser):
    parser_root_actions = [action for action in parser._actions
                           if isinstance(action, argparse._SubParsersAction)]

    for root_action in parser_root_actions:
        for choice, subparser in root_action.choices.items():
            subparser_actions = [action for action in subparser._actions
                                 if isinstance(action, argparse._SubParsersAction)]
            for subparser_action in subparser_actions:
                for name, action_obj in subparser_action.choices.items():
                    action_obj.add_argument('-v', '--verbose',
                                            action='count',
                                            default=0,
                                            help="Increase output verbosity. "
                                                 "-v will print debug messages. "
                                                 "-vv will additionally print 3'rd party info")


def show_version():
    import pkgutil
    import json
    data = pkgutil.get_data('fas', 'VERSION')
    version = json.loads(data)['version']
    return version


def create_arguments_parser():
    # Help:
    # https://pymotw.com/2/argparse/

    args_parser = argparse.ArgumentParser(prog='fas')

    subparsers = args_parser.add_subparsers(help='Manage faaSpot account')

    args_root_parsers = list()
    args_root_parsers.append(add_spots_args(subparsers))
    args_root_parsers.append(add_deployments_args(subparsers))
    args_root_parsers.append(add_executions_args(subparsers))
    args_root_parsers.append(add_profiles_args(subparsers))

    show_version()
    args_parser.add_argument('--version', action='version', version=show_version())

    add_verbose_to_all_commands(args_parser)

    return args_parser, args_root_parsers


parser, root_parsers = create_arguments_parser()
