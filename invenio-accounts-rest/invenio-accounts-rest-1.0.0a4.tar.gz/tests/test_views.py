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


"""Test module's REST API."""

from __future__ import absolute_import, print_function

import json
from collections import namedtuple

import pytest
from flask import url_for
from flask_security.utils import verify_password
from invenio_accounts.models import Role, User
from invenio_db import db
from six import iteritems
from six.moves.urllib.parse import parse_qs, urlparse

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def normalize_links(links):
    """Normalize links by parsing them.

    This is needed as query parameters' order is non deterministic.
    """
    def normalize(link):
        """Parse a link in order to make the query string deterministic."""
        parsed_link = urlparse(link)._asdict()
        parsed_link['query'] = parse_qs(parsed_link['query'])
        return parsed_link
    return {
        name: normalize(link) for name, link in iteritems(links)
    }


def test_list_roles(app, users, create_roles, roles_data,
                    accounts_rest_permission_factory):
    """Test listing all existing roles."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.list_roles',
                    page=2,
                    size=2,
                    access_token=access_token,
                ),
                headers=headers
            )
            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))

            def generate_expected_role(idx):
                return {
                    'links': {
                        'self': url_for(
                            'invenio_accounts_rest.role',
                            role_id=create_roles[idx]['id'],
                            _external=True,
                        )
                    },
                    'description': create_roles[idx]['description'],
                    'name': create_roles[idx]['name'],
                    'id': create_roles[idx]['id']
                }

            response_data['links'] = normalize_links(response_data['links'])
            assert response_data == {
                'links': normalize_links({
                    'prev': url_for(
                        'invenio_accounts_rest.list_roles',
                        page=1, size=2, _external=True
                    ),
                    'next': url_for(
                        'invenio_accounts_rest.list_roles',
                        page=3, size=2, _external=True
                    ),
                }),
                'hits': {
                    'hits': [generate_expected_role(idx) for idx in [2, 3]],
                    'total': 10
                }
            }

            # test with a name
            res = client.get(
                url_for(
                    'invenio_accounts_rest.list_roles',
                    page=1,
                    size=2,
                    access_token=access_token,
                    q='ole4'
                ),
                headers=headers
            )
            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            assert len(response_data['hits']['hits']) == 1
            assert response_data['hits']['total'] == 1
            assert response_data['hits']['hits'][0] == \
                generate_expected_role(4)

    with app.app_context():
        allowed_user = users['admin']

        accounts_rest_permission_factory['allowed_users'][
            'read_roles_list'].append(allowed_user.id)

        get_test(allowed_user)


def test_list_too_many_roles(app, users, create_roles, roles_data,
                             accounts_rest_permission_factory):
    """Test requesting too many roles."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        user = users['admin']

        accounts_rest_permission_factory['allowed_users'][
            'read_roles_list'].append(user.id)

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.list_roles',
                    page=1,
                    size=1000000,
                    access_token=access_token,
                ),
                headers=headers
            )

            assert res.status_code == 400


def test_list_roles_permissions(app, users, create_roles, roles_data,
                                accounts_rest_permission_factory):
    """Test permissions for listing roles.

    This is testing the default permission factory.
    Anonymous user cannot read roles.
    Authenticated users can read roles.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.list_roles',
                    access_token=access_token,
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    # anonymous user
    with app.app_context():
        get_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_roles_list'].append(allowed_user.id)

        get_test(allowed_user, 200)

    with app.app_context():
        non_allowed_user = users['user2']
        get_test(non_allowed_user, 403)


def test_read_role(app, users, create_roles, roles_data,
                   accounts_rest_permission_factory):
    """Test getting a role."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user):
        with app.app_context():
            r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=r1.id,
                    access_token=access_token,
                ),
                headers=headers
            )

            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))

            assert response_data == {
                'links': {
                    'self': url_for(
                        'invenio_accounts_rest.role',
                        role_id=r1.id,
                        _external=True
                    )
                },
                'description': r1.description,
                'name': r1.name,
                'id': r1.id
            }

    with app.app_context():
        allowed_user = users['admin']

        r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        accounts_rest_permission_factory['allowed_users']['read_role'][
            allowed_user.id] = [r1.id]

        get_test(allowed_user)


def test_read_role_permissions(app, users, create_roles, roles_data,
                               accounts_rest_permission_factory):
    """Test permissions for getting a role.

    This is testing the default permission factory.
    Anonymous user cannot read roles.
    Authenticated users can read roles.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user, expected_code):
        with app.app_context():
            r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=r1.id,
                    access_token=access_token,
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    # anonymous user
    with app.app_context():
        get_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        with app.app_context():
            r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

            accounts_rest_permission_factory['allowed_users']['read_role'][
                allowed_user.id] = [r1.id]

        get_test(allowed_user, 200)

    with app.app_context():
        non_allowed_user = users['user2']
        get_test(non_allowed_user, 403)


def test_create_role(app, users, create_roles, roles_data,
                     accounts_rest_permission_factory):
    """Test creating a role."""
    counter = [0]

    def post_test(user, expected_code, headers):
        counter[0] += 1
        with app.test_client() as client:
            access_token = user.allowed_token if user else None
            res = client.post(
                url_for(
                    'invenio_accounts_rest.list_roles',
                    access_token=access_token,
                ),
                data=json.dumps({
                    'name': 'testrole{}'.format(counter[0]),
                    'description': 'desc'
                }),
                headers=headers
            )

            assert res.status_code == expected_code
            if expected_code == 201:
                response_data = json.loads(res.get_data(as_text=True))

                role_id = response_data['id']
                assert response_data == {
                    'links': {
                        'self': url_for(
                            'invenio_accounts_rest.role',
                            role_id=role_id,
                            _external=True
                        )
                    },
                    'description': 'desc',
                    'name': 'testrole{}'.format(counter[0]),
                    'id': role_id
                }

    with app.app_context():
        allowed_user = users['admin']

        accounts_rest_permission_factory['allowed_users'][
            'create_role'].append(allowed_user.id)
        # test with valid content type
        post_test(allowed_user, 201, [
            ('Content-Type', 'application/json'),
            ('Accept', 'application/json')
        ])
        # test with unknown content type
        post_test(allowed_user, 406, [
            ('Content-Type', 'application/unknown'),
            ('Accept', 'application/json')
        ])


def test_create_role_permissions(app, users, create_roles, roles_data,
                                 accounts_rest_permission_factory):
    """Test creating a role permissions.

    This is testing the default permission factory.
    Anonymous user cannot create a role.
    Allowed user and admin can create a role.
    Authenticated users cannot create roles.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def post_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.post(
                url_for(
                    'invenio_accounts_rest.list_roles',
                    access_token=access_token,
                ),
                data=json.dumps(
                    {'name': 'role', 'description': 'desc'}
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        post_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'create_role'].append(allowed_user.id)

        post_test(allowed_user, 201)

    with app.app_context():
        non_allowed_user = users['user2']
        post_test(non_allowed_user, 403)


def test_delete_role(app, users, create_roles, roles_data,
                     accounts_rest_permission_factory):
    """Test deleting a role."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def delete_test(user, role_id):
        with app.app_context():
            r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.delete(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=r1.id,
                    access_token=access_token,
                ),
                headers=headers
            )
            assert res.status_code == 204

            res = client.get(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=r1.id
                ),
                headers=headers
            )
            assert res.status_code == 404

    with app.app_context():
        allowed_user = users['admin']

        role_name = roles_data[0]['name']
        role_id = Role.query.filter_by(name=role_name).one().id

        accounts_rest_permission_factory['allowed_users']['delete_role'][
            allowed_user.id] = [role_id]

        delete_test(allowed_user, role_id)


def test_delete_role_permissions(app, users, create_roles, roles_data,
                                 accounts_rest_permission_factory):
    """Test permissions for deleting a role.

    This is testing the default permission factory.
    Anonymous user cannot delete a role.
    Allowed user and admin can delete a role.
    Authenticated users cannot delete roles.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def delete_test(user, expected_code, role_id):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.delete(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=role_id,
                    access_token=access_token,
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        # unauthenticated user cannot delete a role
        role_name = roles_data[0]['name']
        role_id = Role.query.filter_by(name=role_name).one().id

        delete_test(None, 401, role_id)

    with app.app_context():
        # role is still in database
        allowed_user = users['user1']
        role_name = roles_data[0]['name']
        role_id = Role.query.filter_by(name=role_name).one().id

        accounts_rest_permission_factory['allowed_users']['delete_role'][
            allowed_user.id] = [role_id]

        delete_test(allowed_user, 204, role_id)

    with app.app_context():
        # role is being added to database again,
        # but non-allowed user cannot delete it
        non_allowed_user = users['admin']

        ds = app.extensions['invenio-accounts'].datastore
        new_role = ds.create_role(**roles_data[0])
        db.session.add(new_role)
        db.session.commit()

        role_name = roles_data[0]['name']
        role_id = Role.query.filter_by(name=role_name).one().id

        delete_test(non_allowed_user, 403, role_id)


def test_assign_role(app, users, create_roles, roles_data,
                     accounts_rest_permission_factory):
    """Test assigning role to user."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        user = users['admin']

        accounts_rest_permission_factory['allowed_users']['assign_role'][
            user.id] = [
            (User.query.get(users['user1'].id).roles[0].id, users['user2'].id)]

        accounts_rest_permission_factory['allowed_users'][
            'read_user_roles_list'][user.id] = [user.id]

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            added_role_id = User.query.get(users['user1'].id).roles[0].id

            res = client.put(
                url_for(
                    'invenio_accounts_rest.assign_role',
                    user_id=users['user2'].id,
                    role_id=added_role_id,
                    access_token=access_token,
                ),
                headers=headers
            )
            assert res.status_code == 200

    with app.app_context():
        user_roles = User.query.get(users['user2'].id).roles
        assert added_role_id in [role.id for role in user_roles]


def test_assign_role_permissions(app, users, create_roles, roles_data,
                                 accounts_rest_permission_factory):
    """Test permissions for assigning a role to a user.

    The call is idempotent (it is expected to succeed even when the user has
    the role already assigned).

    This is testing the default permission factory.
    Anonymous user cannot assign a role.
    Allowed user and admin can assign a role.
    Authenticated users cannot assign roles.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def put_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.put(
                url_for(
                    'invenio_accounts_rest.assign_role',
                    user_id=users['user2'].id,
                    role_id=User.query.get(users['user1'].id).roles[0].id,
                    access_token=access_token,
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        put_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']
        accounts_rest_permission_factory['allowed_users']['assign_role'][
            allowed_user.id] = [
            (User.query.get(users['user1'].id).roles[0].id, users['user2'].id)]
        put_test(allowed_user, 200)

    with app.app_context():
        other_user = users['user2']
        put_test(other_user, 403)


def test_unassign_role(app, users, create_roles, roles_data,
                       accounts_rest_permission_factory):
    """Test unassigning role from user."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        user = users['admin']

        accounts_rest_permission_factory['allowed_users']['unassign_role'][
            user.id] = [
            (User.query.get(users['user1'].id).roles[0].id, users['user1'].id)]

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            deleted_role_id = User.query.get(users['user1'].id).roles[0].id

            res = client.delete(
                url_for(
                    'invenio_accounts_rest.assign_role',
                    user_id=users['user1'].id,
                    role_id=deleted_role_id,
                    access_token=access_token,
                ),
                headers=headers
            )
            assert res.status_code == 204

    with app.app_context():
        user_roles = User.query.get(users['user1'].id).roles
        assert deleted_role_id not in [role.id for role in user_roles]


def test_unassign_role_permissions(app, users, create_roles, roles_data,
                                   accounts_rest_permission_factory):
    """Test permissions for unassigning a role from a user.

    The call is idempotent (it is expected to succeed even when the user has
    the role already unassigned).

    This is testing the default permission factory.
    Anonymous user cannot unassign a role.
    Allowed user and admin can unassign a role.
    Authenticated users cannot unassign roles.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def delete_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.delete(
                url_for(
                    'invenio_accounts_rest.assign_role',
                    user_id=users['user1'].id,
                    role_id=User.query.get(users['user1'].id).roles[0].id,
                    access_token=access_token,
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        delete_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']
        accounts_rest_permission_factory['allowed_users']['unassign_role'][
            allowed_user.id] = [
            (User.query.get(users['user1'].id).roles[0].id, users['user1'].id)]
        delete_test(allowed_user, 204)

    with app.app_context():
        other_user = users['user2']
        delete_test(other_user, 403)


@pytest.mark.parametrize("headers,patch", [
    (
        [('Content-Type', 'application/json-patch+json'),
         ('Accept', 'application/json')],
        [{
            'op': 'replace',
            'path': '/name',
            'value': 'new_name'
        }, {
            'op': 'replace',
            'path': '/description',
            'value': 'new_desc'
        }]
    ), (
        [('Content-Type', 'application/json'),
         ('Accept', 'application/json')],
        {
            'name': 'new_name',
            'description': 'new_desc'
        }
    )
])
def test_update_role(app, users, create_roles, roles_data,
                     accounts_rest_permission_factory, headers, patch):
    """Test updating a role."""

    def patch_test(user):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

            res = client.patch(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=r1.id,
                    access_token=access_token,
                ),
                data=json.dumps(patch),
                headers=headers
            )

            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            assert response_data == {
                'links': {
                    'self': url_for(
                        'invenio_accounts_rest.role',
                        role_id=r1.id,
                        _external=True
                    )
                },
                'description': 'new_desc',
                'name': 'new_name',
                'id': r1.id
            }

    with app.app_context():
        allowed_user = users['admin']
        r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        accounts_rest_permission_factory['allowed_users']['update_role'][
            allowed_user.id] = [r1.id]

        patch_test(allowed_user)


def test_update_role_permissions(app, users, create_roles, roles_data,
                                 accounts_rest_permission_factory):
    """Test permissions for updating a role.

    This is testing the default permission factory.
    Anonymous user cannot update a role.
    Allowed user and admin can update a role.
    Authenticated users cannot update roles.
    """
    headers = [('Content-Type', 'application/json-patch+json'),
               ('Accept', 'application/json')]

    def patch_test(user, expected_code):
        with app.app_context():
            r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.patch(
                url_for(
                    'invenio_accounts_rest.role',
                    role_id=r1.id,
                    access_token=access_token,
                ),
                data=json.dumps([{
                    'op': 'replace',
                    'path': '/name',
                    'value': 'new_name'
                }]),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        patch_test(None, 401)

    with app.app_context():
        other_user = users['user2']
        patch_test(other_user, 403)

    with app.app_context():
        allowed_user = users['user1']
        r1 = Role.query.filter_by(name=roles_data[0]['name']).one()

        accounts_rest_permission_factory['allowed_users']['update_role'][
            allowed_user.id] = [r1.id]

        patch_test(allowed_user, 200)


def test_get_user_roles(app, users, create_roles, roles_data,
                        accounts_rest_permission_factory):
    """Test listing all users roles."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None
            u1 = User.query.filter_by(id=users['user1'].id).one()

            res = client.get(
                url_for(
                    'invenio_accounts_rest.user_roles_list',
                    user_id=u1.id,
                    access_token=access_token,
                    size=2, page=2
                ),
                headers=headers
            )

            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            response_data['links'] = normalize_links(response_data['links'])
            assert response_data == {
                'hits': {
                    'hits': [{
                        'links': {
                            'self': url_for(
                                'invenio_accounts_rest.role',
                                role_id=role.id,
                                _external=True
                            )
                        },
                        'id': role.id,
                        'description': role.description,
                        'name': role.name,
                    } for role in sorted(
                        u1.roles, key=lambda role: role.name)[2:4]],
                    'total': 5,
                },
                'links': normalize_links({
                    'prev': url_for(
                        'invenio_accounts_rest.user_roles_list',
                        user_id=user.id, page=1, size=2, _external=True
                    ),
                    'next': url_for(
                        'invenio_accounts_rest.user_roles_list',
                        user_id=user.id, page=3, size=2, _external=True
                    ),
                })
            }

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_user_roles_list'][allowed_user.id] = [allowed_user.id]

        get_test(allowed_user)


def test_get_too_many_user_roles(app, users, create_roles, roles_data,
                                 accounts_rest_permission_factory):
    """Test listing too many users roles."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_user_roles_list'][user.id] = [user.id]

        with app.test_client() as client:
            access_token = user.allowed_token if user else None
            u1 = User.query.filter_by(id=users['user1'].id).one()

            res = client.get(
                url_for(
                    'invenio_accounts_rest.user_roles_list',
                    user_id=users['user1'].id,
                    access_token=access_token,
                    size=1000000,
                ),
                headers=headers
            )

            assert res.status_code == 400


def test_get_user_roles_permissions(app, users, create_roles, roles_data,
                                    accounts_rest_permission_factory):
    """Test permissions for getting an user's roles.

    This is testing the default permission factory.
    Anonymous user cannot get a role.
    Allowed user and admin can get a role.
    Authenticated users cannot get role.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.user_roles_list',
                    user_id=users['user1'].id,
                    access_token=access_token,
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        get_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_user_roles_list'][allowed_user.id] = [allowed_user.id]

        get_test(allowed_user, 200)

    with app.app_context():
        other_user = users['user2']
        get_test(other_user, 403)


@pytest.mark.parametrize('app', [
    {'with_profiles': True}, {'with_profiles': False}
], indirect=['app'])
def test_get_user_properties(app, with_profiles, users, create_roles,
                             roles_data, accounts_rest_permission_factory):
    """Test listing all user's properties."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.user',
                    user_id=users['user1'].id,
                    access_token=access_token
                ),
                headers=headers
            )

            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            expected = {
                'id': users['user1'].id,
                'email': 'user1@inveniosoftware.org',
                'active': True,
                'links': {
                    'self': url_for(
                        'invenio_accounts_rest.user',
                        user_id=users['user1'].id,
                        _external=True
                    )
                }
            }
            if with_profiles:
                expected.update({
                    'full_name': users['user1'].data['profile']['full_name'],
                    'username': users['user1'].data['profile']['username'],
                })

            assert response_data == expected

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_user_properties'][allowed_user.id] = [allowed_user.id]

        get_test(allowed_user)


def test_get_user_properties_permissions(app, users, create_roles, roles_data,
                                         accounts_rest_permission_factory):
    """Test permissions for getting a user account's properties.

    This is testing the default permission factory.
    Anonymous user cannot get user's properties.
    Allowed user and admin can get user's properties.
    Authenticated users cannot get user's properties.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.user',
                    user_id=users['user1'].id,
                    access_token=access_token
                ),
                headers=headers
            )

        assert res.status_code == expected_code

    with app.app_context():
        get_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_user_properties'][allowed_user.id] = [allowed_user.id]

        get_test(allowed_user, 200)

    with app.app_context():
        other_user = users['user2']
        get_test(other_user, 403)


@pytest.mark.parametrize('app', [
    {'with_profiles': True}, {'with_profiles': False}
], indirect=['app'])
def test_update_user_properties(app, with_profiles, users, create_roles,
                                roles_data, accounts_rest_permission_factory):
    """Test modifying user's properties."""
    json_headers = [('Content-Type', 'application/json'),
                    ('Accept', 'application/json')]
    json_patch_headers = [('Content-Type', 'application/json-patch+json'),
                          ('Accept', 'application/json')]

    with app.app_context():
        def create_patch(idx):
            """Create both a simple patch and a JSON PATCH."""
            patch = {'email': 'other{}@email.com'.format(idx)}
            if with_profiles:
                patch['full_name'] = 'other_full_name'
                patch['username'] = 'other_username{}'.format(idx)

            # create a JSON patch matching the previous patch object
            json_patch = [
                {"op": "replace", "path": "/{}".format(key), "value": value}
                for key, value in patch.items()
            ]
            return (patch, json_patch)

        def test_patch(user, applied_patch, expected_patch, headers):
            """Test the modification of the given user's properties."""
            accounts_rest_permission_factory['allowed_users'][
                'update_user_properties'][user.id] = [user.id]
            with app.test_client() as client:
                access_token = user.allowed_token if user else None

                res = client.patch(
                    url_for(
                        'invenio_accounts_rest.user',
                        user_id=user.id,
                        access_token=access_token,
                    ),
                    data=json.dumps(applied_patch),
                    headers=headers
                )

                assert res.status_code == 200
                response_data = json.loads(res.get_data(as_text=True))
                expected_user = {
                    'id': user.id,
                    'email': expected_patch['email'],
                    'active': True,
                    'links': {
                        'self': url_for(
                            'invenio_accounts_rest.user',
                            user_id=user.id,
                            _external=True
                        )
                    }
                }
                if with_profiles:
                    expected_user.update({
                        'full_name': expected_patch['full_name'],
                        'username': expected_patch['username'],
                    })
                assert response_data == expected_user
        patch, _ = create_patch(0)
        # test with a simple JSON object as data
        test_patch(users['user1'], patch, patch, json_headers)
        patch, json_patch = create_patch(1)
        # test with JSON-patch as data
        test_patch(users['user2'], json_patch, patch, json_patch_headers)


def test_invalid_update_user_properties(app, users, create_roles, roles_data,
                                        accounts_rest_permission_factory):
    """Test modifying user's properties with an invalid field."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'update_user_properties'][user.id] = [user.id]

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.patch(
                url_for(
                    'invenio_accounts_rest.user',
                    user_id=users['user1'].id,
                    access_token=access_token,
                ),
                data=json.dumps({
                    'unknown': 'field'
                }),
                headers=headers
            )

            assert res.status_code == 400


def test_update_user_properties_permissions(app, users,
                                            accounts_rest_permission_factory):
    """Test permissions for modifying a user account's properties.

    This is testing the default permission factory.
    Anonymous user cannot modify user's properties.
    Allowed user and admin can modify user's properties.
    Authenticated users cannot modify user's properties.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def patch_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.patch(
                url_for(
                    'invenio_accounts_rest.user',
                    user_id=users['user1'].id,
                    access_token=access_token,
                ),
                data=json.dumps({'email': 'other@email.com'}),
                headers=headers
            )
        assert res.status_code == expected_code

    with app.app_context():
        patch_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'update_user_properties'][allowed_user.id] = [allowed_user.id]

        patch_test(allowed_user, 200)

    with app.app_context():
        other_user = users['user2']
        patch_test(other_user, 403)


def test_change_user_password(app, users, create_roles, roles_data,
                              accounts_rest_permission_factory):
    """Test changing user's password."""
    headers = [('Content-Type', 'application/json-patch+json'),
               ('Accept', 'application/json')]

    def patch_test(user):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.patch(
                url_for(
                    'invenio_accounts_rest.user',
                    user_id=users['user1'].id,
                    access_token=access_token,
                ),
                data=json.dumps([
                    {"op": "replace", "path": "/email",
                     "value": 'other@email.com'},
                    {"op": "add", "path": "/old_password",
                     "value": 'pass1'},
                    {"op": "replace", "path": "/password",
                     "value": 'other_pass'},
                ]),
                headers=headers
            )

            assert res.status_code == 200
            assert verify_password('other_pass', User.query.get(
                users['user1'].id).password) is True

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'update_user_properties'][allowed_user.id] = [allowed_user.id]

        patch_test(allowed_user)


def test_invalid_change_user_password(app, users, create_roles, roles_data,
                                      accounts_rest_permission_factory):
    """Test changing user's password without providing the old one."""
    headers = [('Content-Type', 'application/json-patch+json'),
               ('Accept', 'application/json')]

    def patch_test(user):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.patch(
                url_for(
                    'invenio_accounts_rest.user',
                    user_id=users['user1'].id,
                    access_token=access_token,
                ),
                data=json.dumps([
                    {"op": "replace", "path": "/password",
                     "value": 'other_pass'},
                ]),
                headers=headers
            )

            assert res.status_code == 400

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'update_user_properties'][allowed_user.id] = [allowed_user.id]

        patch_test(allowed_user)


def test_list_users_permissions(app, users, create_roles, roles_data,
                                accounts_rest_permission_factory):
    """Test permissions for listing users.

    This is testing the default permission factory.
    Anonymous user cannot list users.
    Allowed user and admin can list users.
    Authenticated users cannot list users.
    """
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    def get_test(user, expected_code):
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.users_list',
                    access_token=access_token,
                ),
                headers=headers,
            )

        assert res.status_code == expected_code

    with app.app_context():
        get_test(None, 401)

    with app.app_context():
        allowed_user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_users_list'].append(allowed_user.id)
        get_test(allowed_user, 200)

    with app.app_context():
        not_allowed_user = users['user2']
        get_test(not_allowed_user, 403)


def test_list_too_many_users(app, users, create_roles, roles_data,
                             accounts_rest_permission_factory):
    """Test listing too many users."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    with app.app_context():
        user = users['user1']

        accounts_rest_permission_factory['allowed_users'][
            'read_users_list'].append(user.id)
        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.users_list',
                    access_token=access_token,
                    size=1000000
                ),
                headers=headers,
            )

        assert res.status_code == 400


@pytest.mark.parametrize('app', [
    {'with_profiles': True}, {'with_profiles': False}
], indirect=['app'])
def test_user_search(app, with_profiles, users, create_roles, roles_data,
                     accounts_rest_permission_factory):
    """Test REST API for circulation specific user search."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    # Search while not being authorized
    with app.app_context():
        other_user = users['user2']
        with app.test_client() as client:
            user = User.query.all()[0]

            url = url_for(
                'invenio_accounts_rest.users_list',
                q=str(user.id + 1),
                access_token=None
            )
            res = client.get(url)

        assert res.status_code == 401

    with app.app_context():
        other_user = users['user2']
        accounts_rest_permission_factory['allowed_users'][
            'read_users_list'].append(other_user.id)
        db.session.commit()

    # Search for non existing user
    with app.app_context():
        with app.test_client() as client:
            user = User.query.all()[0]
            other_user = users['user2']

            url = url_for(
                'invenio_accounts_rest.users_list',
                q=1000,
                access_token=other_user.allowed_token
            )
            res = client.get(url, headers=headers)
            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            assert len(response_data['hits']['hits']) == 0

    # Search for existing user
    with app.app_context():
        with app.test_client() as client:
            user = User.query.all()[0]
            other_user = users['user2']

            url = url_for(
                'invenio_accounts_rest.users_list',
                q=user.email,
                access_token=other_user.allowed_token
            )
            res = client.get(url, headers=headers)

            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            assert len(response_data['hits']['hits']) == 1

    # Search for all
    with app.app_context():
        user = users['user2']

        with app.test_client() as client:
            access_token = user.allowed_token if user else None

            res = client.get(
                url_for(
                    'invenio_accounts_rest.users_list',
                    access_token=access_token,
                    size=2, page=2,
                ),
                headers=headers,
            )
            assert res.status_code == 200
            response_data = json.loads(res.get_data(as_text=True))
            response_data['links'] = normalize_links(response_data['links'])

            assert response_data == {
                'links': normalize_links({
                    'prev': url_for(
                        'invenio_accounts_rest.users_list',
                        page=1, size=2, _external=True
                    ),
                    'next': url_for(
                        'invenio_accounts_rest.users_list',
                        page=3, size=2, _external=True
                    ),
                }),
                'hits': {
                    'hits': [expected_user(user, with_profiles) for user in
                             sorted(users.values(),
                                    key=lambda user: user.data['email'])[2:4]],
                    'total': 9
                }
            }


@pytest.mark.parametrize('app', [
    {'with_profiles': True}, {'with_profiles': False}
], indirect=['app'])
def test_role_users_search(app, with_profiles, users, create_roles, roles_data,
                           accounts_rest_permission_factory):
    """Test searching users having a specific role assigned."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]

    # assign the role to 'user1, user2 and user3'
    with app.app_context():
        role = Role.query.filter(Role.id == create_roles[0]['id']).one()
        assigned_users = [users[username] for username in
                          ['user{}'.format(idx) for idx in range(1, 6)]]
        user_models = User.query.filter(
            User.id.in_(user.id for user in assigned_users)
        ).all()
        for model in user_models:
            if role not in model.roles:
                model.roles.append(role)
        db.session.commit()

        url = url_for(
            'invenio_accounts_rest.role_users_list',
            role_id=role.id,
            access_token=users['user1'].allowed_token, page=2, size=2
        )
        accounts_rest_permission_factory['allowed_users'][
            'read_role_users_list'][users['user1'].id] = [role.id]

    with app.test_client() as client:
        res = client.get(url, headers=headers)
        assert res.status_code == 200
        response_data = json.loads(res.get_data(as_text=True))

        response_data['links'] = normalize_links(response_data['links'])

    with app.app_context():
        assert response_data == {
            'links': normalize_links({
                'prev': url_for(
                    'invenio_accounts_rest.role_users_list',
                    role_id=role.id,
                    page=1, size=2, _external=True
                ),
                'next': url_for(
                    'invenio_accounts_rest.role_users_list',
                    role_id=role.id,
                    page=3, size=2, _external=True
                ),
            }),
            'hits': {
                'hits': [expected_user(user, with_profiles) for user in
                         sorted(assigned_users,
                                key=lambda user: user.data['email'])[2:4]],
                'total': 5
            }
        }

    with app.app_context():
        url = url_for(
            'invenio_accounts_rest.role_users_list',
            role_id=role.id, q='user1',
            access_token=users['user1'].allowed_token
        )
    # test filtering by name
    with app.test_client() as client:
        res = client.get(url, headers=headers)
        assert res.status_code == 200
        response_data = json.loads(res.get_data(as_text=True))
        assert response_data['hits']['total'] == 1
        assert response_data['hits']['hits'][0]['id'] == users['user1'].id


def test_role_users_search_permissions(app, users, create_roles, roles_data,
                                       accounts_rest_permission_factory):
    """Test permissions of searching users having a specific role assigned."""
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    with app.app_context():
        role = Role.query.filter(Role.id == create_roles[0]['id']).one()

    def test_role_user_search(user, expected_code):
        url = url_for(
            'invenio_accounts_rest.role_users_list',
            role_id=role.id,
            access_token=user.allowed_token if user is not None else None
        )

        with app.test_client() as client:
            res = client.get(url, headers=headers)
            assert res.status_code == expected_code

    with app.app_context():
        accounts_rest_permission_factory['allowed_users'][
            'read_role_users_list'][users['user1'].id] = [role.id]

        test_role_user_search(None, 401)
        test_role_user_search(users['user2'], 403)
        test_role_user_search(users['user1'], 200)


def expected_user(user, with_profiles):
    """Serialize user as expected."""
    expected_user = {
        'id': user.id,
        'email': user.data['email'],
        'active': True,
        'links': {
            'self': url_for(
                'invenio_accounts_rest.user',
                user_id=user.id,
                _external=True
            )
        }
    }
    if with_profiles:
        expected_user.update({
            'full_name': user.data['profile']['full_name'],
            'username': user.data['profile']['username'],
        })
    return expected_user
