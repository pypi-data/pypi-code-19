from signal import signal, SIGPIPE, SIG_DFL
import logging

import click
from prody import confProDy, LOGGER

from . import make_cli_class
from ..version import version

from .util import config


def make_subcommand(package):
    @click.command(package, cls=make_cli_class(package))
    def cli():
        pass
    return cli


@click.group('sblu')
@click.option('-v', '--verbose', count=True)
@click.version_option(version=version)
def cli(verbose):
    signal(SIGPIPE, SIG_DFL)

    level = logging.ERROR
    if verbose >= 1:
        level = logging.WARNING
    if verbose >= 2:
        level = logging.INFO
    if verbose >= 3:
        level = logging.DEBUG

    logging.basicConfig(level=level)
    LOGGER._setverbosity(confProDy('verbosity'))


for subcommand in ('pdb', 'docking', 'measure', 'cluspro', 'ftmap'):
    sub_cli = make_subcommand(subcommand)
    cli.add_command(sub_cli)

cli.add_command(config)
