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
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

from django_pgpmailman.views.list import (
    pgp_list_index, pgp_list_summary,
    ListSignatureSettingsView, ListEncryptionSettingsView,
    ListMiscSettingsView, ListKeyManagementView, ListPubkey, ListPrivkey,
    ListCreate)
from django_pgpmailman.views.user import UserSummaryView

list_patterns = [
    url(r'^$', pgp_list_summary, name='pgp_list_summary'),
    url(r'^key/$',
        ListKeyManagementView.as_view(success_url='pgp_list_key_management'),
        name='pgp_list_key_management'),
    url(r'^signatures/$', ListSignatureSettingsView.as_view(
            success_url='pgp_list_signature_settings'),
        name='pgp_list_signature_settings'),
    url(r'^encryption/$', ListEncryptionSettingsView.as_view(
            success_url='pgp_list_encryption_settings'),
        name='pgp_list_encryption_settings'),
    url(r'^misc/$',
        ListMiscSettingsView.as_view(success_url='pgp_list_misc_settings'),
        name='pgp_list_misc_settings'),
    url(r'^pubkey$', ListPubkey.as_view(), name='pgp_list_pubkey'),
    url(r'^privkey$', ListPrivkey.as_view(), name='pgp_list_privkey')
]

user_patterns = [
    url(r'^$', UserSummaryView.as_view(),
        name='pgp_user_profile')
]

urlpatterns = [
    url(r'^$', pgp_list_index, name='pgp_list_index'),
    url(r'^lists/create/$', ListCreate.as_view(success_url='pgp_list_summary'),
        name='pgp_list_create'),
    url(r'^lists/(?P<list_id>[^/]+)/', include(list_patterns)),
    url(r'^accounts/', include(user_patterns))
]
