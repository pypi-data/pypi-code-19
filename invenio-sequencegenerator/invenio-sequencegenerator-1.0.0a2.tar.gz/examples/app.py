# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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


"""Minimal Flask application example for development.

Run example development server:

.. code-block:: console
    $ cd examples
    $ export FLASK_APP=app.py
    $ flask db init
    $ flask db create
    $ flask fixtures sequences
    $ flask run --debugger

"""

from __future__ import absolute_import, print_function

import os

from flask import Flask
from flask_admin import Admin
from flask_babelex import Babel
from invenio_db import InvenioDB, db
from invenio_sequencegenerator.admin import counter_adminview as ca
from invenio_sequencegenerator.admin import templatedefinition_adminview as ta
from invenio_sequencegenerator.api import Sequence, Template
# Create Flask application
from invenio_sequencegenerator.ext import InvenioSequenceGenerator

app = Flask(__name__)
app.config.update(
    SECRET_KEY="CHANGE_ME",
    SECURITY_PASSWORD_SALT="CHANGE_ME_ALSO",
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
)
Babel(app)
InvenioDB(app)
InvenioSequenceGenerator(app)


@app.cli.group()
def fixtures():
    """Command for working with test data."""


@fixtures.command()
def sequences():
    """Load test data fixture."""
    pl = Template.create('PL', '{year}: Playlist {counter}', start=1)
    fl = Template.create('FL', '{PL} > Audio File {counter:02d}', start=1)
    pl15 = Sequence(pl, year=2015)
    pl15.next()
    pl15.next()
    pl16 = Sequence(pl, year=2016)
    pl16.next()
    fl15 = Sequence(fl, PL='2015: Playlist 2')
    fl15.next()
    fl15.next()
    fl16 = Sequence(fl, PL='2016: Playlist 1')
    fl16.next()
    db.session.commit()


@app.route('/')
def index():
    """Simple home page."""
    return '<a href="/admin/">Click me to get to Admin!</a>'


# Create admin
admin = Admin(app, name='Example: Sequence Generator',
              template_mode='bootstrap3')

# Add views
admin.add_view(ta['modelview'](ta['model'], db.session))
admin.add_view(ca['modelview'](ca['model'], db.session))
