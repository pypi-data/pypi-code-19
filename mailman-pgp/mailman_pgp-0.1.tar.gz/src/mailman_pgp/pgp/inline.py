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

from pgpy import PGPKey, PGPMessage
from pgpy.constants import SymmetricKeyAlgorithm
from pgpy.types import Armorable
from public import public


@public
class InlineWrapper:
    """Inline PGP wrapper."""

    def __init__(self, msg):
        """
        Wrap the given message.

        :param msg: The message to wrap.
        :type msg: mailman.email.message.Message
        """
        self.msg = msg

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
        for part in walk(self.msg):
            if not part.is_multipart() and self._is_signed(part):
                try:
                    msg = PGPMessage.from_blob(part.get_payload()).message
                except:
                    continue
                yield msg

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

    def _has_keys(self, part):
        try:
            dearm = Armorable.ascii_unarmor(part.get_payload())
            if dearm['magic'] in ('PUBLIC KEY BLOCK', 'PRIVATE KEY BLOCK'):
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

    def _keys(self, part):
        try:
            # TODO: potentially return all things returned from from_blob?
            key, _ = PGPKey.from_blob(part.get_payload())
            return key
        except:
            pass

    def keys(self):
        """
        Get the collection of keys in this message.

        :return: A collection of keys.
        """
        yield from self._walk(self._keys)

    def _verify(self, part, key):
        try:
            message = PGPMessage.from_blob(part.get_payload())
            return key.verify(message)
        except:
            pass
        return False

    def verify(self, key):
        """
        Verify the signature of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signatures.
        :rtype: Generator[pgpy.types.SignatureVerification]
        """
        for part in walk(self.msg):
            if not part.is_multipart() and self._is_signed(part):
                yield self._verify(part, key)

    def _sign(self, pmsg, key, hash):
        smsg = copy.copy(pmsg)
        smsg |= key.sign(smsg, hash=hash)
        return smsg

    def sign(self, key, hash=None):
        """
        Sign a message with key.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :param hash: The hash algorithm to use.
        :type hash: pgpy.constants.HashAlgorithm
        :return: The signed message.
        :rtype: mailman.email.message.Message
        """
        out = copy.deepcopy(self.msg)
        for part in walk(out):
            if not part.is_multipart():
                payload = str(part.get_payload())
                pmsg = PGPMessage.new(payload, cleartext=True)
                smsg = self._sign(pmsg, key, hash)
                part.set_payload(str(smsg))
        return out

    def _decrypt(self, part, key):
        message = PGPMessage.from_blob(part.get_payload())
        decrypted = key.decrypt(message)
        if decrypted.is_signed:
            part.set_payload(str(decrypted))
        else:
            part.set_payload(decrypted.message)

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return: The decrypted message.
        :rtype: mailman.email.message.Message
        """
        out = copy.deepcopy(self.msg)
        for part in walk(out):
            if not part.is_multipart() and self._is_encrypted(part):
                self._decrypt(part, key)
        return out

    def _encrypt(self, pmsg, *keys, cipher):
        emsg = copy.copy(pmsg)
        if len(keys) == 1:
            emsg = keys[0].encrypt(emsg, cipher=cipher)
        else:
            session_key = cipher.gen_key()
            for key in keys:
                emsg = key.encrypt(emsg, cipher=cipher,
                                   session_key=session_key)
            del session_key
        return emsg

    def encrypt(self, *keys, cipher=SymmetricKeyAlgorithm.AES256):
        """
        Encrypt the message with key/s, using cipher.

        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param cipher: The symmetric cipher to use.
        :type cipher: SymmetricKeyAlgorithm
        :return: mailman.email.message.Message
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        out = copy.deepcopy(self.msg)
        for part in walk(out):
            if not part.is_multipart():
                payload = str(part.get_payload())
                pmsg = PGPMessage.new(payload)
                emsg = self._encrypt(pmsg, *keys, cipher=cipher)
                part.set_payload(str(emsg))
        return out

    def sign_encrypt(self, key, *keys, hash=None,
                     cipher=SymmetricKeyAlgorithm.AES256):
        """

        :param key:
        :param keys:
        :param hash:
        :param cipher:
        :return:
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        out = copy.deepcopy(self.msg)
        for part in walk(out):
            if not part.is_multipart():
                payload = str(part.get_payload())
                pmsg = PGPMessage.new(payload)
                smsg = self._sign(pmsg, key, hash=hash)
                emsg = self._encrypt(smsg, *keys, cipher=cipher)
                part.set_payload(str(emsg))
        return out

    def sign_then_encrypt(self, key, *keys, hash=None,
                          cipher=SymmetricKeyAlgorithm.AES256):
        # TODO: sign into cleartext here and then encrypt? I mean that's weird
        # but thats what sing *then* encrypt means for inline pgp.
        return self.sign_encrypt(key, *keys, hash=hash, cipher=cipher)
