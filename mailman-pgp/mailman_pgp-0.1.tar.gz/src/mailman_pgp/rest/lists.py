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
from mailman.interfaces.listmanager import IListManager
from mailman.rest.helpers import (
    child, CollectionMixin, etag, not_found, okay)
from public import public
from zope.component import getUtility

from mailman_pgp.config import config
from mailman_pgp.model.list import PGPMailingList


class _EncryptedBase(CollectionMixin):
    def _resource_as_dict(self, emlist):
        """See `CollectionMixin`."""
        return dict(list_id=emlist.list_id,
                    unsigned_msg_action=emlist.unsigned_msg_action,
                    inline_pgp_action=emlist.inline_pgp_action,
                    expired_sig_action=emlist.expired_sig_action,
                    revoked_sig_action=emlist.revoked_sig_action,
                    invalid_sig_action=emlist.invalid_sig_action,
                    strip_original_sig=emlist.strip_original_sig,
                    sign_outgoing=emlist.sign_outgoing,
                    nonencrypted_msg_action=emlist.nonencrypted_msg_action,
                    self_link=self.api.path_to(
                            '/plugins/{}/lists/{}'.format(config.name,
                                                          emlist.list_id)))

    def _get_collection(self, request):
        """See `CollectionMixin`."""
        return PGPMailingList.query().all()


@public
class AllEncryptedLists(_EncryptedBase):
    def on_get(self, request, response):
        """/lists"""
        resource = self._make_collection(request)
        return okay(response, etag(resource))


@public
class AnEncryptedList(_EncryptedBase):
    def __init__(self, list_identifier):
        manager = getUtility(IListManager)
        if '@' in list_identifier:
            mlist = manager.get(list_identifier)
        else:
            mlist = manager.get_by_list_id(list_identifier)
        self._mlist = PGPMailingList.for_list(mlist)

    def on_get(self, request, response):
        """/lists/<list_id>"""
        if self._mlist is None:
            return not_found(response)
        else:
            okay(response, self._resource_as_json(self._mlist))

    @child()
    def pubkey(self, context, segments):
        return AListPubkey(self._mlist), []


@public
class AListPubkey:
    def __init__(self, mlist):
        self._mlist = mlist

    def on_get(self, request, response):
        """/lists/<list_id>/key"""
        if self._mlist is None:
            return not_found(response)
        else:
            pubkey = self._mlist.pubkey
            if pubkey is None:
                return not_found(response)

            resource = dict(public_key=str(pubkey),
                            key_fingerprint=str(pubkey.fingerprint))
            return okay(response, etag(resource))
