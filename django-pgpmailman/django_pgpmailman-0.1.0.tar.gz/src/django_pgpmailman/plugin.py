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
from operator import itemgetter

from django.conf import settings
from mailmanclient import Plugin, Client

from django_pgpmailman.models import PGPMailingList, PGPAddress


class PGPPlugin(Plugin):
    def __init__(self, base_plugin):
        super(PGPPlugin, self).__init__(base_plugin.connection,
                                        base_plugin.name,
                                        base_plugin.rest_data)
        self._base_plugin = base_plugin

    @property
    def lists(self):
        response, content = self.call('lists')
        if 'entries' not in content:
            return []
        return [PGPMailingList(self._connection, entry['self_link'], entry) for
                entry in sorted(content['entries'], key=itemgetter('list_id'))]

    def get_list(self, list_identifier):
        response, content = self.call('lists/%s' % list_identifier)
        return PGPMailingList(self._connection, content['self_link'], content)

    @property
    def addresses(self):
        response, content = self.call('addresses')
        if 'entries' not in content:
            return []
        return [PGPAddress(self._connection, entry['self_link'], entry) for
                entry in sorted(content['entries'], key=itemgetter('email'))]

    def get_address(self, email):
        response, content = self.call('addresses/%s' % email)
        return PGPAddress(self._connection, content['self_link'], content)


def get_client():
    return Client('%s/3.1' %
                  settings.MAILMAN_REST_API_URL,
                  settings.MAILMAN_REST_API_USER,
                  settings.MAILMAN_REST_API_PASS)


plugin = None


def get_plugin():
    global plugin
    if not plugin:
        client = get_client()
        plugin = PGPPlugin(client.get_plugin(settings.MAILMAN_PGP_PLUGIN_NAME))
    return plugin
