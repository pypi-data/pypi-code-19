# -*- coding: utf-8 -*-
"""
numina

Usage:
  numina authenticate <token>
  numina counts <feeds> [--starttime=<starttime> --endtime=<endtime> --class=<class> --bins=<bins>]
  numina movements <feeds> [--starttime=<starttime>|--endtime=<endtime>]
  numina devices
  numina -h | --help

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --starttime=<starttime>           A RFC-3339 timestamp of query starttime, defaults to 7 days before the current time
  --endtime=<endtime>               A RFC-3339 timestamp of query endtime, defaults to the current utc time
  --bins=<bins>                     A time duration literal representing groupings of time - available bins (uµsmhdw), defaults to 1 hour
  --class=<class>                   A comma seperated list of class objects to include in search

Examples:
  numina authenticate 2n3kkd3_234kn.adf&20$9u3.casdf
  numina counts dkkd20994739 --starttime=2017-06-01T15:00:00Z
  numina devices

"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import numina.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items(): 
        if hasattr(numina.commands, k) and v:
            module = getattr(numina.commands, k)
            numina.commands = getmembers(module, isclass)
            command = [command[1] for command in numina.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
