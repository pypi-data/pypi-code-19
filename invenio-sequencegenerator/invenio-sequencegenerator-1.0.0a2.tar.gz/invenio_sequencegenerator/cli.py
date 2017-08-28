# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Click command-line interface for managing sequences."""

from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
from invenio_db import db
from invenio_sequencegenerator.api import Sequence, Template


@click.group()
def sequences():
    """Sequence management commands."""


@sequences.command()
@click.argument('template_name')
@click.argument('meta_template')
@click.option('--start', default=0, help='initial counter')
@click.option('--step', default=1, help='incremental step of the counter')
@with_appcontext
def create(template_name, meta_template, start, step):
    """Create a new template definition."""
    Template.create(template_name, meta_template, start, step)
    db.session.commit()
    click.secho('Template "{0}" created successfully.'.format(template_name),
                fg='green')


@sequences.command(name='next')
@click.argument('template_name')
@click.argument('keywords', nargs=-1)
@with_appcontext
def get_next(template_name, keywords):
    """Get the next counter for a specific sequence."""
    next_counter = Sequence(
        template_name,
        **{k: v for k, v in map(lambda arg: arg.split('='), keywords)}
    ).next()
    db.session.commit()
    click.echo(next_counter)
