"""
                   _______          _ _
  /\_________/\   |__   __|        | | |
 /__\_______/__\     | | ___   ___ | | | __
|    |         |     | |/ _ \ / _ \| | |/ /
|    |  \___/  |     | | (_) | (_) | |   <
|____|_________|     |_|\___/ \___/|_|_|\_\.

==============================================

Usage:
  toolk generate <blueprint> <name>
  toolk -h | --help
  toolk --version
Options:
  -h --help                         Show this screen.
  --version                         Show version.
Examples:
  toolk generate viewcontroller foo
Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/Alphazella/toolk
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import toolk.commands
    options = docopt(__doc__, version=VERSION)
    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(toolk.commands, k) and v:
            module = getattr(toolk.commands, k)
            toolk.commands = getmembers(module, isclass)
            command = [command[1] for command in toolk.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
