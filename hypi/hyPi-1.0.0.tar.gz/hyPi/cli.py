"""
hyPi

Usage:
  hyPi hello
  hyPi -h | --help
  hyPi --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  hyPi hello

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/Shashikant86/hyPi
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import hyPi.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(hyPi.commands, k) and v:
            module = getattr(hyPi.commands, k)
            hyPi.commands = getmembers(module, isclass)
            command = [command[1] for command in hyPi.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
