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

from mailman.rest.helpers import CollectionMixin, etag, not_found, okay
from public.public import public

from mailman_pgp.config import config
from mailman_pgp.model.address import PGPAddress


class _EncryptedBase(CollectionMixin):
    def _resource_as_dict(self, address):
        """See `CollectionMixin`."""
        return dict(email=address.email,
                    key_fingerprint=address.key_fingerprint,
                    key_confirmed=address.key_confirmed,
                    self_link=self.api.path_to(
                            '/plugins/{}/addresses/{}'.format(config.name,
                                                              address.email)
                    ))

    def _get_collection(self, request):
        """See `CollectionMixin`."""
        return PGPAddress.query().all()


@public
class AllAddresses(_EncryptedBase):
    def on_get(self, request, response):
        """/addresses"""
        resource = self._make_collection(request)
        return okay(response, etag(resource))


@public
class AnAddress(_EncryptedBase):
    def __init__(self, email):
        self._address = PGPAddress.for_email(email)

    def on_get(self, request, response):
        if self._address is None:
            return not_found(response)
        else:
            okay(response, self._resource_as_json(self._address))
