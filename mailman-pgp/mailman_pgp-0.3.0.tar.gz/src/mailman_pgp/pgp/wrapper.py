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

"""A combined PGP/MIME + inline PGP wrapper."""

from pgpy.errors import PGPError
from public import public

from mailman_pgp.pgp.base import BaseWrapper
from mailman_pgp.pgp.inline import InlineWrapper
from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.pgp.mime_multisig import MIMEMultiSigWrapper
from mailman_pgp.utils.pgp import verifies


@public
class PGPWrapper(BaseWrapper):
    """A combined PGP/MIME + inline PGP wrapper."""

    def __init__(self, msg, copy=False, default=MIMEWrapper):
        """
        Wrap the given message.

        :param msg: The message to wrap.
        :type msg: mailman.email.message.Message
        :param copy: Whether to copy the message when wrapping.
        :type copy: bool
        :param default: The wrapper class used for active operations (sign,
                        encrypt, attach_keys, attach_revocs)
        :type default: Type[MIMEWrapper|MIMEMultiSigWrapper|InlineWrapper]
        """
        super().__init__(msg, copy)
        self.mime = MIMEWrapper(self.msg)
        self.inline = InlineWrapper(self.msg)
        self.multisig = MIMEMultiSigWrapper(self.msg)
        self.wrappers = (self.mime, self.inline, self.multisig)
        if default is MIMEWrapper:
            self.default = self.mime
        elif default is MIMEMultiSigWrapper:
            self.default = self.multisig
        elif default is InlineWrapper:
            self.default = self.inline
        else:
            raise ValueError('Default wrapper must be one of ' +
                             MIMEWrapper.__name__ + ' ' +
                             MIMEMultiSigWrapper.__name__ + ' ' +
                             InlineWrapper.__name__ + '.')

    def _rewrap(self, wrapper):
        if wrapper is not None:
            return PGPWrapper(wrapper.msg, default=self.default.__class__)

    def get_payload(self):
        return self.default.get_payload()

    def is_signed(self):
        """
        Whether this message is signed.

        :return: If the message is signed.
        :rtype: bool
        """
        return any(wrapper.is_signed() for wrapper in self.wrappers)

    def has_signature(self):
        """
        Whether some parts of the message are signed.

        :return: If some parts of the message are signed.
        :rtype: bool
        """
        return any(wrapper.has_signature() for wrapper in self.wrappers)

    def get_signed(self):
        """
        Get the signed content of the message.

        :return: The signed contents of the message.
        :rtype: typing.Generator[str]
        """
        if self.mime.is_signed():
            yield from self.mime.get_signed()
        elif self.multisig.is_signed():
            yield from self.multisig.get_signed()
        elif self.inline.is_signed():
            yield from self.inline.get_signed()

    def get_signature(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPMessage|pgpy.PGPSignature|
                                 pgpy.PGPDetachedSignature]
        """
        if self.mime.is_signed():
            yield from self.mime.get_signature()
        elif self.multisig.is_signed():
            yield from self.multisig.get_signature()
        elif self.inline.is_signed():
            yield from self.inline.get_signature()

    def strip_signature(self):
        """

        :return:
        :rtype: PGPWrapper
        """
        result = None
        if self.mime.is_signed():
            result = self.mime.strip_signature()
        elif self.multisig.is_signed():
            result = self.multisig.strip_signature()
        elif self.inline.is_signed():
            result = self.inline.strip_signature()
        return self._rewrap(result)

    def sign(self, key, **kwargs):
        """
        Sign a message with key.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :return:
        :rtype: PGPWrapper
        """
        return self._rewrap(self.default.sign(key, **kwargs))

    def verify(self, key):
        """
        Verify the signatures of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signatures.
        :rtype: typing.Generator[pgpy.types.SignatureVerification]
        """
        if self.mime.is_signed():
            yield from self.mime.verify(key)
        elif self.multisig.is_signed():
            yield from self.multisig.verify(key)
        elif self.inline.is_signed():
            yield from self.inline.verify(key)

    def verifies(self, key):
        return verifies(self.verify(key))

    def is_encrypted(self):
        """
        Whether the message is encrypted.

        :return: If the message is encrypted.
        :rtype: bool
        """
        return any(wrapper.is_encrypted() for wrapper in self.wrappers)

    def has_encryption(self):
        """
        Whether some parts of the message are encrypted.

        :return: If some parts of the message are encrypted.
        :rtype: bool
        """
        return any(wrapper.has_encryption() for wrapper in self.wrappers)

    def get_encrypted(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPMessage]
        """
        if self.mime.is_encrypted():
            yield from self.mime.get_encrypted()
        elif self.multisig.is_encrypted():
            yield from self.mime.get_encrypted()
        elif self.inline.is_encrypted():
            yield from self.inline.get_encrypted()

    def encrypt(self, *keys, **kwargs):
        """
        Encrypt the message with key/s, using cipher.

        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :return:
        :rtype: PGPWrapper
        """
        return self._rewrap(self.default.encrypt(*keys, **kwargs))

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :raises: pgpy.errors.PGPError
        :return:
        :rtype: PGPWrapper
        """
        result = None
        if self.mime.is_encrypted():
            result = self.mime.decrypt(key)
        elif self.multisig.is_encrypted():
            result = self.multisig.decrypt(key)
        elif self.inline.is_encrypted():
            result = self.inline.decrypt(key)
        return self._rewrap(result)

    def try_decrypt(self, key):
        """
        Try decrypting the message with given key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return: The decrypted message, if successfully decrypted,
                 else original message.
        :rtype: PGPWrapper
        """
        try:
            return self._rewrap(self.decrypt(key))
        except PGPError:
            return self

    def sign_encrypt(self, key, *keys, **kwargs):
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
        :rtype: PGPWrapper
        """
        return self._rewrap(self.default.sign_encrypt(key, *keys, **kwargs))

    def is_keys(self):
        """
        Whether the message is all keys (all parts).

        :return: If the message is keys.
        :rtype: bool
        """
        return any(wrapper.is_keys() for wrapper in self.wrappers)

    def has_keys(self):
        """
        Whether the message contains public or private keys.

        :return: If the message contains keys.
        :rtype: bool
        """
        return any(wrapper.has_keys() for wrapper in self.wrappers)

    def keys(self):
        """
        Get the collection of keys in this message.

        :return: A collection of keys.
        :rtype: typing.Generator[pgpy.PGPKey]
        """
        if self.mime.has_keys():
            yield from self.mime.keys()
        elif self.multisig.has_keys():
            yield from self.multisig.keys()
        elif self.inline.has_keys():
            yield from self.inline.keys()

    def has_revocs(self):
        """

        :return:
        :rtype: bool
        """
        return any(wrapper.has_revocs() for wrapper in self.wrappers)

    def is_revocs(self):
        """

        :return:
        :rtype: bool
        """
        return any(wrapper.is_revocs() for wrapper in self.wrappers)

    def revocs(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPSignature]
        """
        if self.mime.has_revocs():
            yield from self.mime.revocs()
        elif self.multisig.has_revocs():
            yield from self.multisig.revocs()
        elif self.inline.has_revocs():
            yield from self.inline.revocs()
