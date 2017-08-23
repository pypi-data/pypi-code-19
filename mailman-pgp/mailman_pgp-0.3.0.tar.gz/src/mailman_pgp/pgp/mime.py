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

"""RFC1847 and RFC3156 compliant message wrapped."""
import copy
from email import message_from_string
from email.encoders import encode_7or8bit
from email.iterators import walk
from email.mime.application import MIMEApplication
from email.utils import collapse_rfc2231_value

from mailman.email.message import Message
from pgpy import PGPMessage, PGPSignature
from pgpy.constants import HashAlgorithm, SymmetricKeyAlgorithm
from public import public

from mailman_pgp.pgp.base import BaseWrapper
from mailman_pgp.utils.email import copy_headers
from mailman_pgp.utils.pgp import key_from_blob, revoc_from_blob


@public
class MIMEWrapper(BaseWrapper):
    """PGP/MIME (RFC1847 + RFC3156) compliant wrapper."""

    _signature_subtype = 'pgp-signature'
    _encryption_subtype = 'pgp-encrypted'
    _keys_subtype = 'pgp-keys'

    _signed_type = 'application/' + _signature_subtype
    _encrypted_type = 'application/' + _encryption_subtype
    _keys_type = 'application/' + _keys_subtype

    _signed_multipart = 'multipart/signed'
    _encrypted_multipart = 'multipart/encrypted'

    _signature_preamble = \
        'This is an OpenPGP/MIME signed message (RFC 4880 and 3156)'
    _encryption_preamble = \
        'This is an OpenPGP/MIME encrypted message (RFC 4880 and 3156)'

    def get_payload(self):
        yield self.msg.as_string()

    def _is_mime(self):
        is_multipart = self.msg.is_multipart()
        payloads = len(self.msg.get_payload()) if self.msg.get_payload() else 0

        return is_multipart and payloads == 2

    def is_signed(self):
        """
        Whether the whole message is MIME signed as per RFC3156 section 5.

        :return: If the message is MIME signed.
        :rtype: bool
        """
        if not self._is_mime():
            return False
        second_type = self.msg.get_payload(1).get_content_type()
        protocol_param = collapse_rfc2231_value(self.msg.get_param('protocol',
                                                                   ''))
        content_subtype = self.msg.get_content_subtype()

        return (second_type == MIMEWrapper._signed_type and
                content_subtype == 'signed' and
                protocol_param == MIMEWrapper._signed_type)

    def has_signature(self):
        return self.is_signed()

    def get_signed(self):
        """

        :return:
        """
        yield self.msg.get_payload(0).as_string()

    def get_signature(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPSignature]
        """
        try:
            sig = PGPSignature.from_blob(
                    self.msg.get_payload(1).get_payload())
        except:
            return
        yield sig

    def strip_signature(self):
        """

        :return:
        :rtype: MIMEWrapper
        """
        inner = self.msg.get_payload(0)
        copy_headers(inner, self.msg, True)
        self.msg.set_payload(inner.get_payload())
        return self

    def is_encrypted(self):
        """
        Whether the whole message is MIME encrypted as per RFC3156 section 4.

        :return: If the message is MIME encrypted.
        :rtype: bool
        """
        if not self._is_mime():
            return False
        first_part = self.msg.get_payload(0).as_string()
        first_type = self.msg.get_payload(0).get_content_type()
        second_type = self.msg.get_payload(1).get_content_type()
        content_subtype = self.msg.get_content_subtype()
        protocol_param = collapse_rfc2231_value(self.msg.get_param('protocol',
                                                                   ''))

        return ('Version: 1' in first_part and
                first_type == MIMEWrapper._encrypted_type and
                second_type == 'application/octet-stream' and
                content_subtype == 'encrypted' and
                protocol_param == MIMEWrapper._encrypted_type)

    def has_encryption(self):
        return self.is_encrypted()

    def get_encrypted(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPMessage]
        """
        try:
            msg = PGPMessage.from_blob(self.msg.get_payload(1).get_payload())
        except:
            return
        yield msg

    def is_keys(self):
        """
        Whether the message has only keys as per RFC3156 section 7.

        :return: If the message is keys.
        :rtype: bool
        """
        for part in walk(self.msg):
            if (not part.is_multipart()  # noqa
                and part.get_content_type() != MIMEWrapper._keys_type):
                return False
        return True

    def has_keys(self):
        """
        Whether the message contains keys as per RFC3156 section 7.

        :return: If the message contains keys.
        :rtype: bool
        """
        for part in walk(self.msg):
            if (not part.is_multipart()  # noqa
                and part.get_content_type() == MIMEWrapper._keys_type):
                return True
        return False

    def keys(self):
        """
        Get the collection of keys in this message.

        :return: A collection of keys.
        """
        for part in walk(self.msg):
            if (not part.is_multipart()  # noqa
                and part.get_content_type() == MIMEWrapper._keys_type):
                try:
                    key = key_from_blob(part.get_payload())
                except:
                    continue
                yield key

    def _attach_key_part(self, obj, name, description):
        key_part = MIMEApplication(_data=str(obj),
                                   _subtype=MIMEWrapper._keys_subtype,
                                   _encoder=encode_7or8bit,
                                   name=name)
        key_part.add_header('Content-Description', description)
        key_part.add_header('Content-Disposition', 'attachment',
                            filename=name)
        self.msg.attach(key_part)

    def attach_keys(self, *keys):
        """
        Attach a key to this message, as per RFC3156 section 7.

        :param keys: Keys to attach.
        :type keys: pgpy.PGPKey
        :return:
        :rtype: MIMEWrapper
        """
        if len(keys) == 0:
            return self

        if self.msg.get_content_type() != 'multipart/mixed':
            # wrap in multipart/mixed
            payload = copy.deepcopy(self.msg)
            self.msg.set_payload([])
            self.msg.set_type('multipart/mixed')
            self.msg['MIME-Version'] = '1.0'
            self.msg.attach(payload)

        for key in keys:
            filename = '0x' + key.fingerprint.keyid + '.asc'
            self._attach_key_part(key, filename, 'OpenPGP key')
        return self

    def _is_revoc(self, part):
        if part.get_content_type() != MIMEWrapper._keys_type:
            return False
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
            if (not part.is_multipart()  # noqa
                and part.get_content_type() == MIMEWrapper._keys_type):
                try:
                    revoc = revoc_from_blob(part.get_payload())
                except:
                    continue
                yield revoc

    def attach_revocs(self, *key_revocations):
        """
        Attach a key revocation signature to the message, as a key subpart.

        :param key_revocations: A key revocation signature to attach.
        :type key_revocations: pgpy.PGPSignature
        :return:
        :rtype: MIMEWrapper
        """
        if len(key_revocations) == 0:
            return self

        if self.msg.get_content_type() != 'multipart/mixed':
            # wrap in multipart/mixed
            payload = copy.deepcopy(self.msg)
            self.msg.set_payload([])
            self.msg.set_type('multipart/mixed')
            self.msg['MIME-Version'] = '1.0'
            self.msg.attach(payload)

        for key_revocation in key_revocations:
            filename = '0x' + key_revocation.signer + '.asc'
            self._attach_key_part(key_revocation, filename,
                                  'OpenPGP key revocation')
        return self

    def verify(self, key):
        """
        Verify the signature of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signature.
        :rtype: Generator[pgpy.types.SignatureVerification]
        """
        clear_text = next(iter(self.get_signed()))
        signature = next(iter(self.get_signature()))
        try:
            verification = key.verify(clear_text, signature)
        except:
            return
        yield verification

    def _micalg(self, hash_algo):
        algs = {
            HashAlgorithm.MD5: 'md5',
            HashAlgorithm.SHA1: 'sha1',
            HashAlgorithm.RIPEMD160: 'ripemd160',
            HashAlgorithm.SHA256: 'sha256',
            HashAlgorithm.SHA384: 'sha384',
            HashAlgorithm.SHA512: 'sha512',
            HashAlgorithm.SHA224: 'sha224'
        }
        return 'pgp-' + algs[hash_algo]

    def _wrap_signed(self, msg, signature):
        """
        As per RFC1847 and RFC3156.

        :param msg:
        :param signature:
        """
        self.msg.set_payload([])
        self.msg.attach(msg)
        self.msg.set_type(MIMEWrapper._signed_multipart)
        self.msg.set_param('micalg', self._micalg(signature.hash_algorithm))
        self.msg.set_param('protocol', MIMEWrapper._signed_type)
        self.msg.preamble = MIMEWrapper._signature_preamble

        second_part = MIMEApplication(_data=str(signature),
                                      _subtype=MIMEWrapper._signature_subtype,
                                      _encoder=encode_7or8bit,
                                      name='signature.asc')
        second_part.add_header('Content-Description',
                               'OpenPGP digital signature')
        second_part.add_header('Content-Disposition', 'attachment',
                               filename='signature.asc')
        self.msg.attach(second_part)

    def sign(self, key, **kwargs):
        """
        Sign a message with key.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :rtype: MIMEWrapper
        """
        payload = next(iter(self.get_payload()))
        signature = key.sign(payload, **kwargs)
        original_msg = copy.deepcopy(self.msg)
        self._wrap_signed(original_msg, signature)

        return self

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return: The decrypted message.
        :rtype: mailman.email.message.Message
        """
        pmsg = next(iter(self.get_encrypted()))
        decrypted = key.decrypt(pmsg)

        dmsg = decrypted.message
        if isinstance(dmsg, bytearray):
            dmsg = dmsg.decode(decrypted.charset or 'utf-8')

        out = message_from_string(dmsg, _class=Message)
        if decrypted.is_signed:
            # rewrap, self.msg should be multipart/signed,
            # headers from out should overwrite those from self.msg
            # self.msg payload should be [out, sig]
            signature = next(iter(decrypted.signatures))
            self._wrap_signed(out, signature)
        else:
            # self.msg payload should be out.get_payload
            # headers from out should overwrite those from self.msg
            self.msg.set_payload(out.get_payload())
            copy_headers(out, self.msg, True)
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

    def _wrap_encrypted(self, payload):
        self.msg.set_payload([])
        self.msg.set_type(MIMEWrapper._encrypted_multipart)
        self.msg.set_param('protocol', MIMEWrapper._encrypted_type)
        self.msg.preamble = MIMEWrapper._encryption_preamble
        first_part = MIMEApplication(_data='Version: 1',
                                     _subtype=MIMEWrapper._encryption_subtype,
                                     _encoder=encode_7or8bit)
        first_part.add_header('Content-Description',
                              'PGP/MIME version identification')
        self.msg.attach(first_part)
        second_part = MIMEApplication(_data=str(payload),
                                      _subtype='octet-stream',
                                      _encoder=encode_7or8bit,
                                      name='encrypted.asc')
        second_part.add_header('Content-Description',
                               'OpenPGP encrypted message')
        second_part.add_header('Content-Disposition', 'inline',
                               filename='encrypted.asc')
        self.msg.attach(second_part)

    def encrypt(self, *keys, cipher=SymmetricKeyAlgorithm.AES256,
                **kwargs):
        """
        Encrypt the message with key/s, using cipher.

        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param cipher: The symmetric cipher to use.
        :type cipher: pgpy.constants.SymmetricKeyAlgorithm
        :return:
        :rtype: MIMEWrapper
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        if self.is_signed():
            # self.msg payload should be [ version_1, encrypted]
            # headers should remain the same, except Content-Type
            # signature should be combined into the PGP blob
            pmsg = PGPMessage.new(next(iter(self.get_signed())))
            pmsg |= next(iter(self.get_signature()))
        else:
            # self.msg payload should be [ version_1, encrypted]
            # headers should remain the same, except Content-Type
            pmsg = PGPMessage.new(next(iter(self.get_payload())))
        pmsg = self._encrypt(pmsg, *keys, cipher=cipher, **kwargs)
        self._wrap_encrypted(pmsg)
        return self

    def sign_encrypt(self, key, *keys, hash=None,
                     cipher=SymmetricKeyAlgorithm.AES256,
                     **kwargs):
        """
        Sign and encrypt the message, in one go.

        This is as per RFC 3156 section 6.2 - Combined method.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param hash:
        :type hash: pgpy.constants.HashAlgorithm
        :param cipher:
        :type cipher: pgpy.constants.SymmetricKeyAlgorithm
        :return:
        :rtype: MIMEWrapper
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        payload = next(iter(self.get_payload()))
        pmsg = PGPMessage.new(payload)
        pmsg |= key.sign(pmsg, hash=hash)
        pmsg = self._encrypt(pmsg, *keys, cipher=cipher, **kwargs)
        self._wrap_encrypted(pmsg)
        return self
