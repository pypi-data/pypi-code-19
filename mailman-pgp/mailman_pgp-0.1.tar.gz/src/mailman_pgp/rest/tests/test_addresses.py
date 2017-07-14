# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
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

""""""
import unittest
from urllib.error import HTTPError

from mailman.interfaces.usermanager import IUserManager
from mailman.testing.helpers import call_api
from zope.component import getUtility

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.testing.layers import PGPRESTLayer


class TestAddresses(unittest.TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        self.mm_address = getUtility(IUserManager).create_address(
                'anne@example.com')
        with transaction() as t:
            self.address = PGPAddress(self.mm_address)
            t.add(self.address)

    def test_missing_address(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/addresses/'
                     'bart@example.com')
        self.assertEqual(cm.exception.code, 404)

    def test_all_addresses(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/addresses/')
        self.assertEqual(json['total_size'], 1)
        self.assertEqual(len(json['entries']), 1)
        addresses = json['entries']
        address = addresses[0]
        self.assertEqual(address['email'], self.address.email)

    def test_get_address(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/addresses/'
                'anne@example.com')
        self.assertEqual(json['email'], self.address.email)
