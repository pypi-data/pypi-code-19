# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from __future__ import print_function
import click

from . import __version__ as version
from .initialize import init


@click.group()
def cli():
    """Entry point for the global management tools"""
    click.echo('Giraumon Tools version: %s' % version)  # pragma: no cover


cli.add_command(init)
