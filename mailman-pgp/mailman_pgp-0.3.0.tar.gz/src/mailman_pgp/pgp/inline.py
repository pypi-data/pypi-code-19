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

"""Strict inline PGP message wrapper."""
import copy
from email.iterators import walk
from email.mime.text import MIMEText

from pgpy import PGPMessage
from pgpy.constants import SymmetricKeyAlgorithm
from public import public

from mailman_pgp.pgp.base import BaseWrapper
from mailman_pgp.utils.pgp import key_from_blob, revoc_from_blob


@public
class InlineWrapper(BaseWrapper):
    """Inline PGP wrapper."""

    def get_payload(self):
        for part in walk(self.msg):
            if not part.is_multipart():
                yield part.get_payload()

    def _walk(self, walk_fn, *args, **kwargs):
        for part in walk(self.msg):
            if not part.is_multipart():
                yield walk_fn(part, *args, **kwargs)

    def _is_signed(self, part):
        try:
            msg = PGPMessage.from_blob(part.get_payload())
            return msg.is_signed
        except:
            pass
        return False

    def is_signed(self):
        """
        Whether the message is inline signed.

        :return: If the message is inline signed.
        :rtype: bool
        """
        return all(self._walk(self._is_signed))

    def has_signature(self):
        """
        Whether some parts of the message are inline signed.

        :return: If some parts of the message are inline signed.
        :rtype: bool
        """
        return any(self._walk(self._is_signed))

    def get_signed(self):
        """

        :return:
        """
        for part in walk(self.msg):
            if not part.is_multipart() and self._is_signed(part):
                try:
                    msg = PGPMessage.from_blob(part.get_payload()).message
                except:
                    continue
                yield msg

    def get_signature(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPMessage]
        """
        for part in walk(self.msg):
            if not part.is_multipart():
                try:
                    msg = PGPMessage.from_blob(part.get_payload())
                except:
                    continue
                yield msg

    def strip_signature(self):
        for part in walk(self.msg):
            if not part.is_multipart() and self._is_signed(part):
                try:
                    msg = PGPMessage.from_blob(part.get_payload())
                except:
                    continue
                part.set_payload(msg.message)
        return self

    def _is_encrypted(self, part):
        try:
            msg = PGPMessage.from_blob(part.get_payload())
            return msg.is_encrypted
        except:
            pass
        return False

    def is_encrypted(self):
        """
        Whether the message is inline encrypted.

        :return: If the message is inline encrypted.
        :rtype: bool
        """
        return all(self._walk(self._is_encrypted))

    def has_encryption(self):
        """
        Whether some parts of the message are inline encrypted.

        :return: If some parts of the message are inline encrypted.
        :rtype: bool
        """
        return any(self._walk(self._is_encrypted))

    def get_encrypted(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPMessage]
        """
        for part in walk(self.msg):
            if not part.is_multipart():
                try:
                    msg = PGPMessage.from_blob(part.get_payload())
                except:
                    continue
                yield msg

    def _has_keys(self, part):
        try:
            key_from_blob(part.get_payload())
            return True
        except:
            pass
        return False

    def is_keys(self):
        """
        Whether the message is all keys (all parts).

        :return: If the message is keys.
        :rtype: bool
        """
        return all(self._walk(self._has_keys))

    def has_keys(self):
        """
        Whether the message contains public or private keys.

        :return: If the message contains keys.
        :rtype: bool
        """
        return any(self._walk(self._has_keys))

    def keys(self):
        """
        Get the collection of keys in this message.

        :return: A collection of keys.
        :rtype: Generator[pgpy.PGPKey]
        """
        for part in walk(self.msg):
            if not part.is_multipart():
                try:
                    key = key_from_blob(part.get_payload())
                except:
                    continue
                yield key

    def _is_revoc(self, part):
        try:
            revoc_from_blob(part.get_payload())
        except ValueError:
            return False
        return True

    def is_revocs(self):
        for part in walk(self.msg):
            if (not part.is_multipart() and not self._is_revoc(part)):
                return False
        return True

    def has_revocs(self):
        for part in walk(self.msg):
            if (not part.is_multipart() and self._is_revoc(part)):
                return True
        return False

    def revocs(self):
        for part in walk(self.msg):
            if not part.is_multipart():
                try:
                    revoc = revoc_from_blob(part.get_payload())
                except:
                    continue
                yield revoc

    def attach_revocs(self, *key_revocations):
        """
        Attach a key revocation signature to the message.

        :param key_revocations: A key revocation signature to attach.
        :type key_revocations: pgpy.PGPSignature
        :return:
        :rtype: InlineWrapper
        """
        if self.msg.get_content_type() != 'multipart/mixed':
            # wrap in multipart/mixed
            payload = copy.deepcopy(self.msg)
            self.msg.set_payload([])
            self.msg.set_type('multipart/mixed')
            self.msg['MIME-Version'] = '1.0'
            self.msg.attach(payload)

        for key_revocation in key_revocations:
            revoc_part = MIMEText(str(key_revocation))
            self.msg.attach(revoc_part)
        return self

    def verify(self, key):
        """
        Verify the signatures of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signatures.
        :rtype: Generator[pgpy.types.SignatureVerification]
        """
        yield from map(key.verify, self.get_signature())

    def _sign(self, pmsg, key, **kwargs):
        smsg = copy.copy(pmsg)
        smsg |= key.sign(smsg, **kwargs)
        return smsg

    def sign(self, key, **kwargs):
        """
        Sign a message with key.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :return:
        :rtype: InlineWrapper
        """
        for part in walk(self.msg):
            if not part.is_multipart():
                if self._is_signed(part):
                    pmsg = PGPMessage.from_blob(part.get_payload())
                else:
                    payload = str(part.get_payload())
                    pmsg = PGPMessage.new(payload, cleartext=True)
                smsg = self._sign(pmsg, key, **kwargs)
                part.set_payload(str(smsg))
        return self

    def _decrypt(self, part, key):
        message = PGPMessage.from_blob(part.get_payload())
        decrypted = key.decrypt(message)
        if decrypted.is_signed:
            part.set_payload(str(decrypted))
        else:
            dmsg = decrypted.message
            if isinstance(dmsg, bytearray):
                dmsg = dmsg.decode(decrypted.charset or 'utf-8')
            part.set_payload(dmsg)

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return:
        :rtype: InlineWrapper
        """
        for part in walk(self.msg):
            if not part.is_multipart() and self._is_encrypted(part):
                self._decrypt(part, key)
        return self

    def _encrypt(self, pmsg, *keys, cipher, **kwargs):
        emsg = copy.copy(pmsg)
        if len(keys) == 1:
            emsg = keys[0].encrypt(emsg, cipher=cipher, **kwargs)
        else:
            session_key = cipher.gen_key()
            for key in keys:
                emsg = key.encrypt(emsg, cipher=cipher,
                                   sessionkey=session_key,
                                   **kwargs)
            del session_key
        return emsg

    def encrypt(self, *keys, cipher=SymmetricKeyAlgorithm.AES256,
                **kwargs):
        """
        Encrypt the message with key/s, using cipher.

        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param cipher: The symmetric cipher to use.
        :type cipher: SymmetricKeyAlgorithm
        :return:
        :rtype: InlineWrapper
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        for part in walk(self.msg):
            if not part.is_multipart():
                payload = str(part.get_payload())
                pmsg = PGPMessage.new(payload)
                emsg = self._encrypt(pmsg, *keys, cipher=cipher, **kwargs)
                part.set_payload(str(emsg))
        return self

    def sign_encrypt(self, key, *keys, hash=None,
                     cipher=SymmetricKeyAlgorithm.AES256,
                     **kwargs):
        """
        Sign and encrypt the message, in one go.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param hash:
        :type hash: pgpy.constants.HashAlgorithm
        :param cipher:
        :type cipher: pgpy.constants.SymmetricKeyAlgorithm
        :return:
        :rtype: InlineWrapper
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        for part in walk(self.msg):
            if not part.is_multipart():
                if self._is_signed(part):
                    pmsg = PGPMessage.from_blob(part.get_payload())
                else:
                    payload = str(part.get_payload())
                    pmsg = PGPMessage.new(payload)
                smsg = self._sign(pmsg, key, hash=hash)
                emsg = self._encrypt(smsg, *keys, cipher=cipher, **kwargs)
                part.set_payload(str(emsg))
        return self
