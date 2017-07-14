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

from os.path import exists, isfile, join

from flufl.lock import Lock
from mailman.database.types import Enum, SAUnicode
from mailman.interfaces.action import Action
from mailman.interfaces.listmanager import IListManager
from pgpy import PGPKey
from public import public
from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.orm import reconstructor
from zope.component import getUtility

from mailman_pgp.config import config
from mailman_pgp.model.base import Base
from mailman_pgp.pgp.keygen import ListKeyGenerator


@public
class PGPMailingList(Base):
    """A PGP enabled mailing list."""

    __tablename__ = 'pgp_lists'

    id = Column(Integer, primary_key=True)
    list_id = Column(SAUnicode, index=True)

    # Signature related properties
    unsigned_msg_action = Column(Enum(Action))
    inline_pgp_action = Column(Enum(Action))
    expired_sig_action = Column(Enum(Action))
    revoked_sig_action = Column(Enum(Action))
    # duplicate_sig_action = Column(Enum(Action))
    invalid_sig_action = Column(Enum(Action))
    strip_original_sig = Column(Boolean)
    sign_outgoing = Column(Boolean)

    # Encryption related properties
    nonencrypted_msg_action = Column(Enum(Action))

    def __init__(self, mlist):
        super().__init__()
        self._init()
        self._defaults()
        self.list_id = mlist.list_id
        self._mlist = mlist

    def _defaults(self):
        self.unsigned_msg_action = Action.reject
        self.inline_pgp_action = Action.defer
        self.expired_sig_action = Action.reject
        self.revoked_sig_action = Action.reject
        self.invalid_sig_action = Action.reject
        self.strip_original_sig = False
        self.sign_outgoing = False

        self.nonencrypted_msg_action = Action.reject

    @reconstructor
    def _init(self):
        self._mlist = None
        self._key = None
        self._key_generator = None

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
    def key(self):
        """

        :return:
        :rtype: pgpy.PGPKey
        """
        if self._key is None:
            # Check the file
            if exists(self.key_path) and isfile(self.key_path):
                self._key, _ = PGPKey.from_file(self.key_path)
        return self._key

    @key.setter
    def key(self, value):
        with Lock(self.key_path + '.lock'):
            self._key = value
            with open(self.key_path, 'w') as key_file:
                key_file.write(str(value))

    def generate_key(self, block=False):
        self._key = None
        self._key_generator = ListKeyGenerator(config.pgp.keypair_config,
                                               self.mlist.display_name,
                                               self.mlist.posting_address,
                                               self.mlist.request_address,
                                               self.key_path)
        self._key_generator.start()
        if block:
            self._key_generator.join()
            return self.key

    @property
    def pubkey(self):
        """

        :return:
        :rtype: pgpy.PGPKey
        """
        if self.key is None:
            return None
        return self.key.pubkey

    @property
    def key_path(self):
        """

        :return:
        :rtype: str
        """
        return join(config.pgp.keydir_config['list_keydir'],
                    self.list_id + '.asc')

    @staticmethod
    def for_list(mlist):
        """

        :param mlist:
        :return:
        :rtype: PGPMailingList|None
        """
        if mlist is None:
            return None
        return PGPMailingList.query().filter_by(list_id=mlist.list_id).first()
