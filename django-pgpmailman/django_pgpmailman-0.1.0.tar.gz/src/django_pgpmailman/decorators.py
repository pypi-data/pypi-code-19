# -*- coding: utf-8 -*-
# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Django Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
from allauth.account.models import EmailAddress
from django.core.exceptions import PermissionDenied
from django.http import Http404
from six import wraps
from six.moves.urllib_error import HTTPError

from django_pgpmailman.plugin import get_plugin, get_client


def list_view(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        try:
            pgp_list = get_plugin().get_list(kwargs.pop('list_id'))
        except HTTPError:
            raise Http404
        return fn(request, pgp_list, *args, **kwargs)

    return wrapper


def list_class_view(fn):
    @wraps(fn)
    def wrapper(self, request, *args, **kwargs):
        self.pgp_list = get_plugin().get_list(kwargs.pop('list_id'))
        return fn(self, request, *args, **kwargs)

    return wrapper


def member_role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated():
                raise PermissionDenied
            mlist = self.pgp_list.mlist
            addresses = set(EmailAddress.objects.filter(
                    user=user, verified=True).values_list('email', flat=True))
            for role in roles:
                for address in addresses:
                    members = mlist.find_members(address, role)
                    if len(members) >= 0:
                        break
                else:
                    raise PermissionDenied

            return fn(self, request, *args, **kwargs)

        return wrapped

    return wrapper


def user_class_view(fn):
    @wraps(fn)
    def wrapper(self, request, *args, **kwargs):
        client = get_client()
        user = request.user
        try:
            self.mm_user = client.get_user(address=user.email)
        except HTTPError:
            self.mm_user = client.create_user(user.email, user.get_full_name())
        return fn(self, request, *args, **kwargs)

    return wrapper
