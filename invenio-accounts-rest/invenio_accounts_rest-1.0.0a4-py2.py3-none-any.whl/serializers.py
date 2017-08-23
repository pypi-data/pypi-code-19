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

"""Invenio accounts REST module's serializers."""

from flask import Response, jsonify, url_for


def role_to_dict(role):
    """Serialize a new role to dict.

    :param role: a new role to serialize into dict.
    :return: dict from role.
    :rtype: dict.
    """
    return dict(
        id=role.id,
        name=role.name,
        description=role.description,
        links=dict(self=role_self_link(role))
    )


def role_self_link(role, **kwargs):
    """Create self link to a given role.

    :param role: a role to to create a self link to.
    :return: link pointing to the given role.
    :rtype: string
    """
    return url_for(
        'invenio_accounts_rest.role',
        role_id=role.id,
        _external=True
    )


def role_serializer(role, code=200, headers=None):
    """Serialize a new role to json response.

    :param role: a new role to serialize.
    :param code: http response code.
    :param headers: additional http response headers.
    :return: response from list of roles.
    :rtype: Response
    """
    response = jsonify(role_to_dict(role))
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


def roles_list_serializer(roles, code=200, headers=None, links=None,
                          total=None):
    """Serialize a list of roles to json response.

    :param roles: a list of roles to serialize.
    :param code: http response code.
    :param headers: additional http response headers.
    :param links: links to paginated pages.
    :param total: number of records
    :return: response from list of roles.
    :rtype: Response
    """
    response = jsonify({
        'hits': {
            'hits': list(map(role_to_dict, roles)),
            'total': total,
        },
        'links': links
    })

    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


def status_code_serializer(code=200, headers=None):
    """Create a response without any content.

    :param code: http response code.
    :param headers: additional http response headers.
    :return: response from api.
    :rtype: Response
    """
    response = Response()
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    return response


def user_self_link(user, **kwargs):
    """Create self link to a given role.

    :param role: a role to to create a self link to.
    :return: link pointing to the given role.
    :rtype: string
    """
    return url_for(
        'invenio_accounts_rest.user',
        user_id=user.id,
        _external=True
    )


def user_to_dict(user):
    """Serialize a new user to dict.

    :param user: a new user to serialize into dict.
    :return: dict from user.
    :rtype: dict
    """
    return dict(
        id=user.id,
        email=user.email,
        active=user.active,
        links=dict(self=user_self_link(user))
    )


def user_with_profile_to_dict(user):
    """Serialize a new user with profile to dict.

    :param user: a new user with profile to serialize into dict.
    :return: dict from user.
    :rtype: dict
    """
    user_dict = dict(
        id=user.id,
        email=user.email,
        active=user.active,
        links=dict(self=user_self_link(user))
    )
    if user.profile:
        user_dict.update(dict(
            full_name=user.profile.full_name,
            username=user.profile.username,
        ))
    return user_dict


def user_serializer_factory(user_to_dict):
    """Serialize a new user to json response.

    :param user_to_dict: a new user to serialize.
    :return: response from list of users.
    :rtype: Response
    """
    def serializer(user, code=200, headers=None):
        response = jsonify(user_to_dict(user))
        response.status_code = code
        if headers is not None:
            response.headers.extend(headers)
        return response
    return serializer


user_serializer = user_serializer_factory(user_to_dict)
user_with_profile_serializer = user_serializer_factory(
    user_with_profile_to_dict)


def users_list_serializer_factory(user_to_dict):
    """Serialize a list of users to json response.

    :param user_to_dict: a new user to serialize
    :return: response from list of users.
    :rtype: Response
    """
    def serializer(users, code=200, headers=None, links=None, total=None):
        if users is None:
            users = []

        response = jsonify({
            'hits': {
                'hits': list(map(user_to_dict, users)),
                'total': total,
            },
            'links': links
        })
        response.status_code = code
        if headers is not None:
            response.headers.extend(headers)
        return response
    return serializer

users_list_serializer = users_list_serializer_factory(user_to_dict)
users_with_profile_list_serializer = users_list_serializer_factory(
    user_with_profile_to_dict)
