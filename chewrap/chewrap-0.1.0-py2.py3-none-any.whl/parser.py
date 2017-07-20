"""Extends ArgumentParser with our own utilities."""

import argparse
import chewrap.arguments
import chewrap.usage
import sys


class ArgumentParser(argparse.ArgumentParser):
    """Class representing the CheWrap argument parser."""

    def add_che_args(self, args):
        """Add arguments to the parser, formatted like CheWrap's arguments.json
        file."""

        for key, arg in args.items():
            if (arg['type'] == 'generic' or arg['type'] == 'bindmount'
                    or arg['type'] == 'env'):
                self.add_generic_che_arg(key, arg)
            elif arg['type'] == 'positional':
                self.add_positional_che_arg(key, arg)
            elif arg['type'] == 'boolean':
                self.add_boolean_che_arg(key, arg)

    def add_generic_che_arg(self, key, arg):
        """Adds a "generic" CheWrap argument.

        "Generic" meaning the default 'action' for Argparse."""

        if 'default' in arg:
            default = arg['default']
        else:
            default = None

        if 'shorthand' in arg:
            self.add_argument(arg['shorthand'], key, help=arg['help'],
                              default=default, metavar=arg['metavar'])
        else:
            self.add_argument(key, help=arg['help'], default=default,
                              metavar=arg['metavar'])

    def add_positional_che_arg(self, key, arg):
        """Adds a positional argument."""

        self.add_argument(key, help=arg['help'])

    def add_boolean_che_arg(self, key, arg):
        """Adds an argument with the 'store_true' or 'store_false' action."""

        if 'shorthand' in arg:
            self.add_argument(arg['shorthand'], key, help=arg['help'],
                              action=arg['action'])
        else:
            self.add_argument(key, help=arg['help'], action=arg['action'])

    def format_usage(self):
        """Get the command's usage."""

        return chewrap.usage.get_usage()

    def print_usage(self, file=None):
        """Print the command's usage."""

        if file is None:
            file = sys.stdout

        self._print_message(self.format_usage(), file)

    def format_help(self):
        """Get the command's full help."""

        return chewrap.usage.get_help()

    def print_help(self, file=None):
        """Print the command's full help."""

        if file is None:
            file = sys.stdout

        self._print_message(self.format_help(), file)
