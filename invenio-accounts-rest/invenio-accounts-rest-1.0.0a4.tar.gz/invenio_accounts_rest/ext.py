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

"""Invenio modules that adds accounts REST API."""

from __future__ import absolute_import, print_function

from flask import current_app

from . import config
from .utils import load_or_import_from_config
from .views import blueprint


class InvenioAccountsREST(object):
    """Invenio-Accounts-REST extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        app.register_blueprint(blueprint)
        app.extensions['invenio-accounts-rest'] = self

    def read_role_permission_factory(self, **kwargs):
        """Permission factory for reading the role."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_READ_ROLE_PERMISSION_FACTORY', app=self.app)

    def update_role_permission_factory(self, **kwargs):
        """Permission factory for updating the role."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_UPDATE_ROLE_PERMISSION_FACTORY', app=self.app)

    def delete_role_permission_factory(self, **kwargs):
        """Permission factory for deleting the role."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_DELETE_ROLE_PERMISSION_FACTORY', app=self.app)

    def read_roles_list_permission_factory(self, **kwargs):
        """Permission factory for reading the list of roles."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_READ_ROLES_LIST_PERMISSION_FACTORY', app=self.app)

    def create_role_permission_factory(self, **kwargs):
        """Permission factory for creating the role."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_CREATE_ROLE_PERMISSION_FACTORY', app=self.app)

    def assign_role_permission_factory(self, **kwargs):
        """Permission factory for assigning the role to the user."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_ASSIGN_ROLE_PERMISSION_FACTORY', app=self.app)

    def unassign_role_permission_factory(self, **kwargs):
        """Permission factory for unassigning the role from the user."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_UNASSIGN_ROLE_PERMISSION_FACTORY', app=self.app)

    def read_role_users_list_permission_factory(self, **kwargs):
        """Permission factory for reading a role's list of users."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_READ_ROLE_USERS_LIST_PERMISSION_FACTORY',
            app=self.app
        )

    def read_user_roles_list_permission_factory(self, **kwargs):
        """Permission factory for reading the list of roles."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_READ_USER_ROLES_LIST_PERMISSION_FACTORY',
            app=self.app
        )

    def read_user_properties_permission_factory(self, **kwargs):
        """Permission factory for reading the user's properties."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_READ_USER_PROPERTIES_PERMISSION_FACTORY',
            app=self.app
        )

    def update_user_properties_permission_factory(self, **kwargs):
        """Permission factory for modifying the user's properties."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_UPDATE_USER_PROPERTIES_PERMISSION_FACTORY',
            app=self.app
        )

    def read_users_list_permission_factory(self, **kwargs):
        """Permission factory for reading the list of users."""
        return load_or_import_from_config(
            'ACCOUNTS_REST_READ_USERS_LIST_PERMISSION_FACTORY', app=self.app)

    def init_config(self, app):
        """Initialize configuration."""
        # Set up API endpoints for records.
        for k in dir(config):
            if k.startswith('ACCOUNTS_REST_'):
                app.config.setdefault(k, getattr(config, k))
