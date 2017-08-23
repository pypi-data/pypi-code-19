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

"""Test default data loader."""

import pytest
from invenio_accounts.models import Role, User
from invenio_rest.errors import RESTValidationError
from werkzeug.exceptions import BadRequest

from invenio_accounts_rest.errors import PatchJSONFailureRESTError
from invenio_accounts_rest.loaders import account_json_patch_loader_factory, \
    default_role_json_patch_loader


def subtest_json_patch_loader(app, loader, input_, known_field):
    # test invalid field
    with app.test_request_context('', data='[{"op": "replace", '
                                  '"path": "/unknown", "value": "v"}]'):
        with pytest.raises(RESTValidationError):
            loader(input_)

    # test invalid JSON PATCH
    with app.test_request_context('', data='[{"op": "replace", '
                                  '"path": "/' + known_field + '"}]'):
        with pytest.raises(PatchJSONFailureRESTError):
            loader(input_)

    # test without data
    with app.test_request_context(''):
        with pytest.raises(BadRequest):
            loader(input_)


def test_account_json_patch_loader_factory_errors(app, users):
    """Test account_json_patch_loader_factory error handling."""
    valid_fields = ['field_A', 'field_B']
    loader = account_json_patch_loader_factory(valid_fields)
    with app.app_context():
        user = User.query.filter(User.id == users['user1'].id).one()
        subtest_json_patch_loader(app, loader, user, 'field_A')


def test_default_role_json_patch_loader_errors(app, create_roles):
    """Test default_role_json_patch_loader error handling."""
    with app.app_context():
        role = Role.query.filter(Role.id == create_roles[0]['id']).one()
        subtest_json_patch_loader(app, default_role_json_patch_loader, role,
                                  'name')
