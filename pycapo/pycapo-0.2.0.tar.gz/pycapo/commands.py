# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse as ap
import sys

from pycapo import CapoConfig, version

_MISSING_PROFILE = """ERROR: pycapo can't deduce the 'profile', give it the -P argument or set the CAPO_PROFILE environment variable! Geeze!\n\n"""

_MISSING_SETTING = """ERROR: missing setting {}.\n"""

_MISSING_OPTION = """ERROR: either -A or a list of settings is needed!\n\n"""

_DESCRIPTION = """Command line Python CAPO interface, version {}. Parses CAPO property files for requested properties, returns them in a format a shell script can use (option name in caps, periods and dashes replaced with underscores)."""

_EPILOG = """Return values:
0: everything worked,
1: can't deduce which profile to use,
2: missing either -A or a list of settings to query,
3: request for missing setting."""


def get_parser():
    r""" Set up and return a parser for this program; note this function is not private because Sphinx needs it to build usage docs.

    :return: parser with arguments and settings in place
    """

    p = ap.ArgumentParser(description=_DESCRIPTION.format(version),
                          formatter_class=ap.RawTextHelpFormatter,
                          epilog=_EPILOG)
    p.add_argument('--path', action='store',
                   help='path of directories to search')
    p.add_argument('--all', '-A', action='store_true',
                   help='display all settings')
    p.add_argument('--quiet', '-q', action='store_true', dest='quiet',
                   help='quiet mode; only display the value')
    p.add_argument('settings', metavar='setting', nargs='*',
                   help='one or more settings to query, ignored if -A ')
    p.add_argument('-P', '--profile', action='store',
                   help='profile name to use, e.g. test, production')
    return p


def _fix_key(key):
    r""" Clean up the option name for use in shell scripts
    """
    return key.replace('.', '_').replace('-', '_')


def _print_option(quiet, key, val, loc):
    r""" Print a result, tersely or verbosely """
    print(val.strip(), end="") if quiet else \
        print("{}=\"{}\" # {}".format(_fix_key(key), val.strip(), loc.strip()))


def pycapo():
    r""" The function what happens when you type pycapo
    """
    parser = get_parser()
    args = parser.parse_args()

    if (not args.all) and len(args.settings) == 0:
        sys.stderr.write(_MISSING_OPTION)
        parser.print_help()
        sys.exit(2)

    # keys for capo properties are stored as uppercase, so convert all the
    # settings to match
    args.settings = [s.upper() for s in args.settings]

    try:
        config = CapoConfig(path=args.path, profile=args.profile)
    except ValueError:
        sys.stderr.write(_MISSING_PROFILE)
        parser.print_help()
        sys.exit(1)

    options, locations = config.getoptions(), config.getlocations()
    d = options if args.all else args.settings
    for key in d:
        try:
            _print_option(args.quiet, key, options[key], locations[key])
        except KeyError:
            sys.stderr.write(_MISSING_SETTING.format(key))
            sys.exit(3)


if __name__ == "__main__":
    pycapo()
