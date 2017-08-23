# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016, 2017 CERN.
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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import tempfile
from collections import namedtuple

import pytest
import six
from flask import Flask
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from flask_mail import Mail
from flask_menu import Menu
from flask_security.utils import hash_password
from invenio_access import InvenioAccess
from invenio_access.models import ActionUsers
from invenio_access.permissions import superuser_access
from invenio_accounts import InvenioAccounts
from invenio_accounts.models import Role, User
from invenio_db import db as db_
from invenio_db import InvenioDB
from invenio_oauth2server import InvenioOAuth2Server, \
    InvenioOAuth2ServerREST, current_oauth2server
from invenio_oauth2server.models import Token
from six import iteritems
from sqlalchemy_utils.functions import create_database, database_exists

from invenio_accounts_rest import InvenioAccountsREST


@pytest.fixture()
def accounts_rest_permission_factory():
    """Permission factory of a module."""
    # will be initialized later as user_id: [role ids]
    allowed_users = {
        'read_role': {},
        'update_role': {},
        'delete_role': {},
        'read_roles_list': [],
        'create_role': [],
        'assign_role': {},
        'unassign_role': {},
        'read_role_users_list': {},
        'read_user_roles_list': {},
        'read_user_properties': {},
        'update_user_properties': {},
        'read_users_list': [],
    }

    def role_permission_factory_sub(action):
        def permission_factory(role):
            from flask_login import current_user
            return (current_user.is_authenticated and
                    current_user.id in allowed_users[action] and
                    role.id in allowed_users[action][current_user.id])
        return lambda role: type('permission_factory', (), {
            'can': lambda self: permission_factory(role)
        })()

    def list_permission_factory_sub(action):
        def l_permission_factory(*args, **kwargs):
            from flask_login import current_user
            return (current_user.is_authenticated and
                    current_user.id in allowed_users[action])

        return lambda: type('permission_factory', (), {
            'can': lambda self: l_permission_factory()
        })()

    def reassign_role_permission_factory_sub(action):
        def rr_permission_factory(role, user):
            from flask_login import current_user
            return (current_user.is_authenticated and
                    current_user.id in allowed_users[action] and
                    (role.id, user.id) in allowed_users[action][
                        current_user.id])

        return lambda role, user: type('permission_factory', (), {
            'can': lambda self: rr_permission_factory(role, user)
        })()

    def user_permission_factory_sub(action):
        def u_permission_factory(user):
            from flask_login import current_user
            return (current_user.is_authenticated and
                    current_user.id in allowed_users[action] and
                    user.id in allowed_users[action][current_user.id])
        return lambda user: type('permission_factory', (), {
            'can': lambda self: u_permission_factory(user)
        })()

    return {
        'read_role': role_permission_factory_sub('read_role'),
        'update_role': role_permission_factory_sub('update_role'),
        'delete_role': role_permission_factory_sub('delete_role'),
        'read_roles_list': list_permission_factory_sub('read_roles_list'),
        'create_role': list_permission_factory_sub('create_role'),
        'assign_role': reassign_role_permission_factory_sub('assign_role'),
        'unassign_role': reassign_role_permission_factory_sub('unassign_role'),
        'read_role_users_list': role_permission_factory_sub(
            'read_role_users_list'),
        'read_user_roles_list': user_permission_factory_sub(
            'read_user_roles_list'),
        'read_user_properties': user_permission_factory_sub(
            'read_user_properties'),
        'update_user_properties': user_permission_factory_sub(
            'update_user_properties'),
        'read_users_list': list_permission_factory_sub('read_users_list'),
        'allowed_users': allowed_users,
    }


@pytest.yield_fixture()
def with_profiles(app):
    """Return True if invenio-userprofiles is installed, else False."""
    return 'invenio-userprofiles' in app.extensions


@pytest.yield_fixture()
def app(request, accounts_rest_permission_factory):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask(__name__, instance_path=instance_path)
    InvenioAccess(app)
    InvenioAccounts(app)
    InvenioAccountsREST(app)
    InvenioOAuth2Server(app)
    InvenioOAuth2ServerREST(app)
    InvenioDB(app)
    Babel(app)
    Mail(app)
    Menu(app)
    Breadcrumbs(app)

    # this is done mainly for coverage so that tests are run with and without
    # userprofiles being loaded in the app
    if not hasattr(request, 'param') or \
            'with_profiles' not in request.param or \
            request.param['with_profiles']:
        # tests without invenio-userprofiles being installed at all
        try:
            from invenio_userprofiles import InvenioUserProfiles
            InvenioUserProfiles(app)
        except ImportError:
            pass

    read_role = accounts_rest_permission_factory['read_role']
    update_role = accounts_rest_permission_factory['update_role']
    delete_role = accounts_rest_permission_factory['delete_role']
    read_roles = accounts_rest_permission_factory['read_roles_list']
    create_role = accounts_rest_permission_factory['create_role']
    assign_role = accounts_rest_permission_factory['assign_role']
    unassign_role = accounts_rest_permission_factory['unassign_role']
    role_users = accounts_rest_permission_factory['read_role_users_list']
    user_roles = accounts_rest_permission_factory['read_user_roles_list']
    read_user_prop = accounts_rest_permission_factory['read_user_properties']
    mod_user_prop = accounts_rest_permission_factory['update_user_properties']
    read_users = accounts_rest_permission_factory['read_users_list']

    app.config.update(
        ACCOUNTS_REST_READ_ROLE_PERMISSION_FACTORY=read_role,
        ACCOUNTS_REST_UPDATE_ROLE_PERMISSION_FACTORY=update_role,
        ACCOUNTS_REST_DELETE_ROLE_PERMISSION_FACTORY=delete_role,
        ACCOUNTS_REST_READ_ROLES_LIST_PERMISSION_FACTORY=read_roles,
        ACCOUNTS_REST_CREATE_ROLE_PERMISSION_FACTORY=create_role,
        ACCOUNTS_REST_ASSIGN_ROLE_PERMISSION_FACTORY=assign_role,
        ACCOUNTS_REST_UNASSIGN_ROLE_PERMISSION_FACTORY=unassign_role,
        ACCOUNTS_REST_READ_ROLE_USERS_LIST_PERMISSION_FACTORY=role_users,
        ACCOUNTS_REST_READ_USER_ROLES_LIST_PERMISSION_FACTORY=user_roles,
        ACCOUNTS_REST_READ_USER_PROPERTIES_PERMISSION_FACTORY=read_user_prop,
        ACCOUNTS_REST_UPDATE_USER_PROPERTIES_PERMISSION_FACTORY=mod_user_prop,
        ACCOUNTS_REST_READ_USERS_LIST_PERMISSION_FACTORY=read_users,
        OAUTH2SERVER_CLIENT_ID_SALT_LEN=40,
        OAUTH2SERVER_CLIENT_SECRET_SALT_LEN=60,
        OAUTH2SERVER_TOKEN_PERSONAL_SALT_LEN=60,
        SECRET_KEY='changeme',
        TESTING=True,
        SERVER_NAME='localhost',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        SECURITY_SEND_PASSWORD_CHANGE_EMAIL=False
    )

    from invenio_oauth2server.views.server import blueprint

    with app.app_context():
        db_.create_all()
    yield app
    with app.app_context():
        db_.drop_all()


@pytest.yield_fixture()
def db(app):
    """Setup database."""
    with app.app_context():
        db_.init_app(app)
        if not database_exists(str(db_.engine.url)):
            create_database(str(db_.engine.url))
        db_.create_all()
    yield db_
    with app.app_context():
        db_.session.remove()
        db_.drop_all()


@pytest.fixture()
def users_data(with_profiles):
    """User data fixture."""
    def user_data(idx):
        data = dict(
            id=41 + idx,
            email='user{}@inveniosoftware.org'.format(idx),
            password='pass1',
            active=True,
        )
        if with_profiles:
            data.update({
                'profile': {
                    'user_id': 41 + idx,
                    'full_name': 'full_name',
                    'username': 'username{}'.format(idx)
                }
            })
        return data

    users = {
        'user{}'.format(idx): user_data(idx) for idx in range(1, 8)
    }
    users.update({
        'inactive': dict(
            id=40,
            email='inactive@inveniosoftware.org',
            password='pass1',
            active=False
        ),
        'admin': {
            "id": 41,
            "email": 'admin@inveniosoftware.org',
            "password": 'pass1',
            "active": True
        }
    })
    return users


@pytest.fixture()
def roles_data():
    """Role data fixture."""
    _roles_data = [
        dict(name='role{}'.format(idx), description='desc{}'.format(idx))
        for idx in range(10)
    ]
    return _roles_data


@pytest.fixture()
def users(app, db, roles_data, users_data, create_roles):
    """Create test users."""
    ds = app.extensions['invenio-accounts'].datastore
    result = {}

    with app.app_context():
        with db.session.begin_nested():

            for user_key, user_data in iteritems(users_data):
                user_data['password'] = hash_password(user_data['password'])
                user = ds.create_user(**user_data)
                result[user_key] = user

            roles = Role.query.filter(
                Role.id.in_(role['id'] for role in create_roles[:5])).all()
            result['user1'].roles.extend(roles)

            db.session.add(ActionUsers.allow(
                superuser_access,
                user=result['admin'],
            ))

            for user in result.values():
                scopes = current_oauth2server.scope_choices()
                db.session.add(user)

                user.allowed_token = Token.create_personal(
                    name='allowed_token',
                    user_id=user.id,
                    scopes=[s[0] for s in scopes]
                ).access_token

            user_ref = namedtuple('UserRef', 'id, allowed_token, data')

            result_user = {
                name: user_ref(
                    id=user.id,
                    data=users_data[name],
                    allowed_token=user.allowed_token,
                ) for name, user in six.iteritems(result)
            }
        db.session.commit()
    return result_user


@pytest.fixture()
def create_roles(app, db, roles_data):
    """Create test roles."""
    ds = app.extensions['invenio-accounts'].datastore

    roles = []
    with app.app_context():
        with db.session.begin_nested():
            for rd in roles_data:
                r = ds.create_role(**rd)
                db.session.add(r)
                roles.append((rd, r))
        db.session.commit()
        for role in roles:
            role[0]['id'] = role[1].id
        return [data for data, role in roles]
