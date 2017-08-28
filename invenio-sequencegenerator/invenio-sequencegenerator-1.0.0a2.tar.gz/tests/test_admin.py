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


"""Test admin view."""

from __future__ import absolute_import, print_function

from flask import url_for
from flask_admin import Admin
from invenio_sequencegenerator.admin import counter_adminview as ca
from invenio_sequencegenerator.admin import templatedefinition_adminview as ta
from invenio_sequencegenerator.api import Sequence, Template


def test_admin(app, db):
    """Test admin interface."""
    assert isinstance(ca, dict)
    assert isinstance(ta, dict)

    assert 'model' in ca
    assert 'modelview' in ca
    assert 'model' in ta
    assert 'modelview' in ta

    # Create admin
    admin = Admin(app, name='Example: Sequence Generator')

    # Add views
    admin.add_view(ta['modelview'](ta['model'], db.session))
    admin.add_view(ca['modelview'](ca['model'], db.session))

    with app.app_context():
        # Create test data
        seq = Sequence(Template.create('ID', 'File {counter}'))
        assert seq.next() == 'File 0'
        assert seq.next() == 'File 1'
        assert seq.next() == 'File 2'
        db.session.commit()

        with app.test_request_context():
            request_url = url_for('counter.reset_view')
        with app.test_client() as client:
            # Reset counter
            client.post(request_url,
                        data={'start': 0, 'rowid': 'File {counter}'},
                        follow_redirects=False)

        # Assert that reset was successful
        assert seq.next() == 'File 0'
