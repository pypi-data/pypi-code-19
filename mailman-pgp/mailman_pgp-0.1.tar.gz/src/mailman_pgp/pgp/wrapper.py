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

from public import public

from mailman_pgp.pgp.inline import InlineWrapper
from mailman_pgp.pgp.mime import MIMEWrapper


@public
class PGPWrapper():
    """A combined PGP/MIME + inline PGP wrapper."""

    def __init__(self, msg, default=MIMEWrapper):
        """
        Wrap the given message.

        :param msg: The message to wrap.
        :type msg: mailman.email.message.Message
        :param default:
        :type default: MIMEWrapper or InlineWrapper
        """
        self.msg = msg
        self.mime = MIMEWrapper(msg)
        self.inline = InlineWrapper(msg)
        if default is MIMEWrapper:
            self.default = self.mime
        elif default is InlineWrapper:
            self.default = self.inline
        else:
            raise ValueError('Default wrapper must be one of ' +
                             MIMEWrapper.__name__ + ' ' +
                             InlineWrapper.__name__ + '.')

    def get_payload(self):
        return self.default.get_payload()

    def is_signed(self):
        return self.mime.is_signed() or self.inline.is_signed()

    def has_signature(self):
        return self.mime.has_signature() or self.inline.has_signature()

    def get_signed(self):
        if self.mime.is_signed():
            yield from self.mime.get_signed()
        elif self.inline.is_signed():
            yield from self.inline.get_signed()

    def sign(self, key, **kwargs):
        return self.default.sign(key, **kwargs)

    def verify(self, key):
        """
        Verify the signature of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signature.
        :rtype: generator of pgpy.types.SignatureVerification
        """
        if self.mime.is_signed():
            yield from self.mime.verify(key)
        elif self.inline.is_signed():
            yield from self.inline.verify(key)

    def verifies(self, key):
        return all(bool(verification) and
                   all(not sigsubj.signature.is_expired
                       for sigsubj in verification.good_signatures) for
                   verification in self.verify(key))

    def is_encrypted(self):
        return self.mime.is_encrypted() or self.inline.is_encrypted()

    def has_encryption(self):
        return self.mime.has_encryption() or self.inline.has_encryption()

    def encrypt(self, *keys, **kwargs):
        return self.default.encrypt(*keys, **kwargs)

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return: The decrypted message.
        :rtype: PGPMessage
        """
        if self.mime.is_encrypted():
            return self.mime.decrypt(key)
        elif self.inline.is_encrypted():
            return self.inline.decrypt(key)

    def is_keys(self):
        return self.mime.is_keys() or self.inline.is_keys()

    def has_keys(self):
        return self.mime.has_keys() or self.inline.has_keys()

    def keys(self):
        """
        Get the collection of keys in this message.

        :return: A collection of keys.
        """
        if self.mime.has_keys():
            yield from self.mime.keys()
        elif self.inline.has_keys():
            yield from self.inline.keys()

    def sign_encrypt(self, key, *keys, **kwargs):
        return self.default.sign_encrypt(key, *keys, **kwargs)

    def sign_then_encrypt(self, key, *keys, **kwargs):
        return self.default.sign_then_encrypt(key, *keys, **kwargs)
