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

"""REST interface to a PGP enabled mailing list."""
from lazr.config import as_boolean
from mailman.interfaces.action import Action
from mailman.interfaces.listmanager import IListManager
from mailman.rest.helpers import (accepted, bad_request,
                                  child, CollectionMixin, etag, GetterSetter,
                                  no_content, not_found, NotFound, okay)
from mailman.rest.validator import (enum_validator, PatchValidator,
                                    UnknownPATCHRequestError, Validator)
from public import public
from zope.component import getUtility

from mailman_pgp.config import config
from mailman_pgp.database import transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.utils.pgp import key_from_blob

CONFIGURATION = dict(
        unsigned_msg_action=GetterSetter(enum_validator(Action)),
        inline_pgp_action=GetterSetter(enum_validator(Action)),
        expired_sig_action=GetterSetter(enum_validator(Action)),
        revoked_sig_action=GetterSetter(enum_validator(Action)),
        invalid_sig_action=GetterSetter(enum_validator(Action)),
        duplicate_sig_action=GetterSetter(enum_validator(Action)),
        strip_original_sig=GetterSetter(as_boolean),
        sign_outgoing=GetterSetter(as_boolean),
        nonencrypted_msg_action=GetterSetter(enum_validator(Action)),
        encrypt_outgoing=GetterSetter(as_boolean)
)


class _PGPListBase(CollectionMixin):
    def _resource_as_dict(self, emlist):
        """See `CollectionMixin`."""
        return dict(list_id=emlist.list_id,
                    unsigned_msg_action=emlist.unsigned_msg_action,
                    inline_pgp_action=emlist.inline_pgp_action,
                    expired_sig_action=emlist.expired_sig_action,
                    revoked_sig_action=emlist.revoked_sig_action,
                    invalid_sig_action=emlist.invalid_sig_action,
                    duplicate_sig_action=emlist.duplicate_sig_action,
                    strip_original_sig=emlist.strip_original_sig,
                    sign_outgoing=emlist.sign_outgoing,
                    nonencrypted_msg_action=emlist.nonencrypted_msg_action,
                    encrypt_outgoing=emlist.encrypt_outgoing,
                    self_link=self.api.path_to(
                            '/plugins/{}/lists/{}'.format(config.name,
                                                          emlist.list_id)))

    def _get_collection(self, request):
        """See `CollectionMixin`."""
        return PGPMailingList.query().all()


@public
class AllPGPLists(_PGPListBase):
    """The PGP enabled mailing lists."""

    def on_get(self, request, response):
        """/lists"""
        resource = self._make_collection(request)
        return okay(response, etag(resource))


@public
class APGPList(_PGPListBase):
    """One PGP enabled mailing list."""

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
            not_found(response)
        else:
            okay(response, self._resource_as_json(self._mlist))

    def on_put(self, request, response):
        """/lists/<list_id>"""
        if self._mlist is None:
            not_found(response)
        else:
            validator = Validator(**CONFIGURATION)
            try:
                with transaction():
                    validator.update(self._mlist, request)
            except ValueError as error:
                bad_request(response, str(error))
            else:
                no_content(response)

    def on_patch(self, request, response):
        """/lists/<list_id>"""
        if self._mlist is None:
            not_found(response)
        else:
            try:
                validator = PatchValidator(request, CONFIGURATION)
            except UnknownPATCHRequestError as error:
                bad_request(
                        response,
                        'Unknown attribute: {}'.format(error.attribute))
                return
            try:
                with transaction():
                    validator.update(self._mlist, request)
            except ValueError as error:
                bad_request(response, str(error))
            else:
                no_content(response)

    @child()
    def key(self, context, segments):
        if self._mlist is None:
            return NotFound(), []
        return AListKey(self._mlist), []

    @child()
    def pubkey(self, context, segments):
        if self._mlist is None:
            return NotFound(), []
        return AListPubkey(self._mlist), []


@public
class AListKey:
    """A PGP private key."""

    def __init__(self, mlist):
        self._mlist = mlist

    def on_get(self, request, response):
        """/lists/<list_id>/key"""
        key = self._mlist.key
        if key is None:
            not_found(response)
        else:
            resource = dict(key=str(key),
                            key_fingerprint=str(key.fingerprint))
            okay(response, etag(resource))

    def on_put(self, request, response):
        """/lists/<list_id>/key"""
        try:
            validator = Validator(key=GetterSetter(key_from_blob))
            values = validator(request)
        except ValueError as error:
            bad_request(response, str(error))
            return
        with transaction():
            self._mlist.key = values.pop('key')
        accepted(response)


@public
class AListPubkey:
    """A PGP list public key."""

    def __init__(self, mlist):
        self._mlist = mlist

    def on_get(self, request, response):
        """/lists/<list_id>/pubkey"""
        pubkey = self._mlist.pubkey
        if pubkey is None:
            not_found(response)
        else:
            resource = dict(public_key=str(pubkey),
                            key_fingerprint=str(pubkey.fingerprint))
            okay(response, etag(resource))
