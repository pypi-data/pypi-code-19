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

"""Model for PGP enabled mailing lists."""
from os import system

from mailman.database.types import Enum, SAUnicode
from mailman.interfaces.action import Action
from mailman.interfaces.listmanager import IListManager, ListDeletingEvent
from mailman.interfaces.member import MemberRole
from public import public
from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.orm import reconstructor
from zope.component import getUtility
from zope.event import classhandler

from mailman_pgp.config import config
from mailman_pgp.database import transaction
from mailman_pgp.database.types import EnumFlag
from mailman_pgp.model.base import Base
from mailman_pgp.model.fs_key import FSKey


@public
class PGPMailingList(Base):
    """A PGP enabled mailing list."""

    __tablename__ = 'pgp_lists'

    id = Column(Integer, primary_key=True)
    list_id = Column(SAUnicode, index=True, unique=True)

    # Signature related properties
    unsigned_msg_action = Column(Enum(Action), default=Action.reject)
    inline_pgp_action = Column(Enum(Action), default=Action.defer)
    expired_sig_action = Column(Enum(Action), default=Action.reject)
    revoked_sig_action = Column(Enum(Action), default=Action.reject)
    invalid_sig_action = Column(Enum(Action), default=Action.reject)
    duplicate_sig_action = Column(Enum(Action), default=Action.reject)
    strip_original_sig = Column(Boolean, default=False)
    sign_outgoing = Column(Boolean, default=False)

    # Encryption related properties
    nonencrypted_msg_action = Column(Enum(Action), default=Action.reject)
    encrypt_outgoing = Column(Boolean, default=True)

    # Key related properties
    key_change_workflow = Column(SAUnicode,
                                 default='pgp-key-change-mod-workflow')
    key_signing_allowed = Column(EnumFlag(MemberRole),
                                 default={MemberRole.owner,
                                          MemberRole.moderator})

    def __init__(self, mlist):
        """

        :param mlist:
        :type mlist: mailman.model.mailinglist.MailingList
        """
        super().__init__(list_id=mlist.list_id)
        self._init()
        self._mlist = mlist

    @reconstructor
    def _init(self):
        self._mlist = None
        self._key = FSKey(config.pgp.keydirs['list_keydir'],
                          self.list_id + '.asc', True)

    @property
    def mlist(self):
        """

        :return:
        :rtype: mailman.model.mailinglist.MailingList
        """
        if self._mlist is None:
            self._mlist = getUtility(IListManager).get_by_list_id(self.list_id)
        return self._mlist

    @property
    def fs_key(self):
        return self._key

    @property
    def key(self):
        """
        The private part of the list's keypair.

        :return:
        :rtype: pgpy.PGPKey
        """
        self._key.reload()
        return self._key.key

    @key.setter
    def key(self, value):
        """

        :param value:
        :type value:
        """
        self._key.key = value
        self._key.save()

    @property
    def pubkey(self):
        """
        The public part of the list's keypair.

        :return:
        :rtype: pgpy.PGPKey
        """
        if self.key is None:
            return None
        return self.key.pubkey

    @property
    def key_path(self):
        """
        The path to this list's key in the `list_keydir`.

        :return: List key path.
        :rtype: str
        """
        return self._key.key_path

    @staticmethod
    def for_list(mlist):
        """

        :param mlist:
        :type mlist: mailman.model.mailinglist.MailingList
        :return:
        :rtype: PGPMailingList|None
        """
        if mlist is None:
            return None
        return PGPMailingList.query().filter_by(list_id=mlist.list_id).first()


@classhandler.handler(ListDeletingEvent)
def on_delete(event):
    shred = config.get_value('keypairs', 'shred')
    shred_command = config.get_value('keypairs', 'shred_command')
    delete = config.get_value('keypairs', 'delete')
    pgp_list = PGPMailingList.for_list(event.mailing_list)
    if pgp_list:
        with transaction() as session:
            if delete:
                if shred:
                    if shred_command:
                        system(shred_command + ' ' + pgp_list.key_path)
                    else:
                        pgp_list.fs_key.shred()
                else:
                    pgp_list.fs_key.delete()
            session.delete(pgp_list)
