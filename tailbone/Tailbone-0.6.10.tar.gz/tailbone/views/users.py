# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
User Views
"""

from __future__ import unicode_literals, absolute_import

import copy

from sqlalchemy import orm

from rattail.db import model
from rattail.db.auth import guest_role, authenticated_role, set_user_password, has_permission

import wtforms
import formalchemy
from formalchemy.fields import SelectFieldRenderer
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views.principal import PrincipalMasterView


def unique_username(value, field):
    user = field.parent.model
    query = Session.query(model.User).filter(model.User.username == value)
    if user.uuid:
        query = query.filter(model.User.uuid != user.uuid)
    if query.count():
        raise formalchemy.ValidationError("Username must be unique.")


def passwords_match(value, field):
    if field.parent.confirm_password.value != value:
        raise formalchemy.ValidationError("Passwords do not match")
    return value


class PasswordFieldRenderer(formalchemy.PasswordFieldRenderer):

    def render(self, **kwargs):
        return tags.password(self.name, value='', maxlength=self.length, **kwargs)


class PasswordField(formalchemy.Field):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('value', lambda x: x.password)
        kwargs.setdefault('renderer', PasswordFieldRenderer)
        kwargs.setdefault('validate', passwords_match)
        super(PasswordField, self).__init__(*args, **kwargs)

    def sync(self):
        if not self.is_readonly():
            password = self.renderer.deserialize()
            if password:
                set_user_password(self.model, password)


def RolesFieldRenderer(request):

    class RolesFieldRenderer(SelectFieldRenderer):

        def render_readonly(self, **kwargs):
            roles = Session.query(model.Role)
            html = ''
            for uuid in self.value:
                role = roles.get(uuid)
                link = tags.link_to(
                    role.name, request.route_url('roles.view', uuid=role.uuid))
                html += HTML.tag('li', c=link)
            html = HTML.tag('ul', c=html)
            return html

    return RolesFieldRenderer


class RolesField(formalchemy.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('options', self.get_options())
        kwargs.setdefault('multiple', True)
        super(RolesField, self).__init__(name, **kwargs)

    def get_value(self, user):
        return [x.uuid for x in user.roles]

    def get_options(self):
        return Session.query(model.Role.name, model.Role.uuid)\
            .filter(model.Role.uuid != guest_role(Session()).uuid)\
            .filter(model.Role.uuid != authenticated_role(Session()).uuid)\
            .order_by(model.Role.name)\
            .all()

    def sync(self):
        if not self.is_readonly():
            user = self.model
            roles = Session.query(model.Role)
            data = self.renderer.deserialize()
            user.roles = [roles.get(x) for x in data]
                

class UsersView(PrincipalMasterView):
    """
    Master view for the User model.
    """
    model_class = model.User
    has_versions = True

    mergeable = True
    merge_additive_fields = [
        'sent_message_count',
        'received_message_count',
    ]
    merge_fields = merge_additive_fields + [
        'uuid',
        'username',
        'person_uuid',
        'person_name',
        'role_count',
        'active',
    ]

    grid_columns = [
        'username',
        'person',
    ]

    def query(self, session):
        return session.query(model.User)\
                      .options(orm.joinedload(model.User.person))

    def configure_grid(self, g):
        super(UsersView, self).configure_grid(g)

        g.joiners['person'] = lambda q: q.outerjoin(model.Person)

        del g.filters['password']
        del g.filters['salt']
        g.filters['username'].default_active = True
        g.filters['username'].default_verb = 'contains'
        g.filters['active'].default_active = True
        g.filters['active'].default_verb = 'is_true'
        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            default_active=True, default_verb='contains')
        g.filters['password'] = g.make_filter('password', model.User.password,
                                              verbs=['is_null', 'is_not_null'])

        g.sorters['person'] = lambda q, d: q.order_by(getattr(model.Person.display_name, d)())
        g.default_sortkey = 'username'

        g.set_label('person', "Person's Name")

    def _preconfigure_fieldset(self, fs):
        fs.username.set(renderer=forms.renderers.StrippedTextFieldRenderer, validate=unique_username)
        fs.person.set(renderer=forms.renderers.PersonFieldRenderer, options=[])
        fs.append(PasswordField('password', label="Set Password"))
        fs.password.attrs(autocomplete='off')
        fs.append(formalchemy.Field('confirm_password', renderer=PasswordFieldRenderer))
        fs.confirm_password.attrs(autocomplete='off')
        fs.append(RolesField('roles', renderer=RolesFieldRenderer(self.request), size=10))

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.username,
                fs.person,
                fs.active,
                fs.active_sticky,
                fs.password,
                fs.confirm_password,
                fs.roles,
            ])
        if self.viewing:
            permissions = self.request.registry.settings.get('tailbone_permissions', {})
            renderer = forms.renderers.PermissionsFieldRenderer(permissions,
                                                                include_guest=True,
                                                                include_authenticated=True)
            fs.append(formalchemy.Field('permissions', renderer=renderer))
        if self.viewing or self.deleting:
            del fs.password
            del fs.confirm_password

    def editable_instance(self, user):
        if self.rattail_config.demo():
            return user.username != 'chuck'
        return True

    def deletable_instance(self, user):
        if self.rattail_config.demo():
            return user.username != 'chuck'
        return True

    def get_version_child_classes(self):
        return [
            (model.UserRole, 'user_uuid'),
        ]

    def find_principals_with_permission(self, session, permission):
        # TODO: this should search Permission table instead, and work backward to User?
        all_users = session.query(model.User)\
                           .filter(model.User.active == True)\
                           .order_by(model.User.username)\
                           .options(orm.joinedload(model.User._roles)\
                                    .joinedload(model.UserRole.role)\
                                    .joinedload(model.Role._permissions))
        users = []
        for user in all_users:
            if has_permission(session, user, permission):
                users.append(user)
        return users

    def get_merge_data(self, user):
        return {
            'uuid': user.uuid,
            'username': user.username,
            'person_uuid': user.person_uuid,
            'person_name': user.person.display_name if user.person else None,
            '_roles': user.roles,
            'role_count': len(user.roles),
            'active': user.active,
            'sent_message_count': len(user.sent_messages),
            'received_message_count': len(user._messages),
        }

    def get_merge_resulting_data(self, remove, keep):
        result = super(UsersView, self).get_merge_resulting_data(remove, keep)
        result['role_count'] = len(set(remove['_roles'] + keep['_roles']))
        return result

    def merge_objects(self, removing, keeping):
        # TODO: merge roles, messages
        assert not removing.sent_messages
        assert not removing._messages
        assert not removing._roles
        self.Session.delete(removing)


def includeme(config):
    UsersView.defaults(config)
