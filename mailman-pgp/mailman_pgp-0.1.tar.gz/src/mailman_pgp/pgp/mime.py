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

from mailman.email.message import Message, MultipartDigestMessage
from pgpy import PGPKey, PGPMessage, PGPSignature
from pgpy.constants import HashAlgorithm, SymmetricKeyAlgorithm
from public import public

from mailman_pgp.pgp.utils import copy_headers


@public
class MIMEWrapper:
    """PGP/MIME (RFC1847 + RFC3156) compliant wrapper."""

    _signature_subtype = 'pgp-signature'
    _encryption_subtype = 'pgp-encrypted'
    _keys_subtype = 'pgp-keys'

    _signed_type = 'application/' + _signature_subtype
    _encrypted_type = 'application/' + _encryption_subtype
    _keys_type = 'application/' + _keys_subtype

    _signature_preamble = \
        'This is an OpenPGP/MIME signed message (RFC 4880 and 3156)'
    _encryption_preamble = \
        'This is an OpenPGP/MIME encrypted message (RFC 4880 and 3156)'

    def __init__(self, msg):
        """
        Wrap the given message.

        :param msg: The message to wrap.
        :type msg: mailman.email.message.Message
        """
        self.msg = msg

    def get_payload(self):
        yield self.msg.as_string()

    def _is_mime(self):
        is_multipart = self.msg.is_multipart()
        payloads = len(self.msg.get_payload())

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
        yield self.msg.get_payload(0).as_string()

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

    def is_keys(self):
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
                key, _ = PGPKey.from_blob(part.get_payload())
                yield key

    def attach_key(self, key):
        """

        :param key:
        :type key: pgpy.PGPKey
        :return:
        """
        filename = '0x' + key.fingerprint.keyid + '.asc'
        key_part = MIMEApplication(_data=str(key),
                                   _subtype=MIMEWrapper._keys_subtype,
                                   _encoder=encode_7or8bit,
                                   name=filename)
        key_part.add_header('Content-Description',
                            'OpenPGP key')
        key_part.add_header('Content-Disposition', 'attachment',
                            filename=filename)
        out = copy.deepcopy(self.msg)
        out.attach(key_part)
        return out

    def verify(self, key):
        """
        Verify the signature of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signature.
        :rtype: Generator[pgpy.types.SignatureVerification]
        """
        clear_text = self.msg.get_payload(0).as_string()
        sig_text = self.msg.get_payload(1).get_payload()
        signature = PGPSignature.from_blob(sig_text)
        yield key.verify(clear_text, signature)

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
        micalg = self._micalg(signature.hash_algorithm)
        out = MultipartDigestMessage('signed', micalg=micalg,
                                     protocol=MIMEWrapper._signed_type)
        out.preamble = MIMEWrapper._signature_preamble

        second_part = MIMEApplication(_data=str(signature),
                                      _subtype=MIMEWrapper._signature_subtype,
                                      _encoder=encode_7or8bit,
                                      name='signature.asc')
        second_part.add_header('Content-Description',
                               'OpenPGP digital signature')
        second_part.add_header('Content-Disposition', 'attachment',
                               filename='signature.asc')

        out.attach(copy.deepcopy(msg))
        out.attach(second_part)
        copy_headers(msg, out)
        return out

    def sign(self, key, hash=None):
        """
        Sign a message with key.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :param hash:
        :type hash: HashAlgorithm
        :return: The signed message.
        :rtype: mailman.email.message.Message
        """
        payload = self.msg.as_string()
        signature = key.sign(payload, hash=hash)
        return self._wrap_signed(self.msg, signature)

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return: The decrypted message.
        :rtype: mailman.email.message.Message
        """
        msg_text = self.msg.get_payload(1).get_payload()
        pmsg = PGPMessage()
        pmsg.parse(msg_text)
        decrypted = key.decrypt(pmsg)

        dmsg = decrypted.message
        if isinstance(dmsg, bytearray):
            dmsg = dmsg.decode(decrypted.charset or 'utf-8')

        out = message_from_string(dmsg, _class=Message)
        if decrypted.is_signed:
            out = self._wrap_signed(out, decrypted.signatures.pop())
        copy_headers(self.msg, out)
        return out

    def _encrypt(self, pmsg, *keys, cipher):
        if len(keys) == 1:
            pmsg = keys[0].encrypt(pmsg, cipher=cipher)
        else:
            session_key = cipher.gen_key()
            for key in keys:
                pmsg = key.encrypt(pmsg, cipher=cipher,
                                   session_key=session_key)
            del session_key
        return pmsg

    def _wrap_encrypted(self, payload):
        out = MultipartDigestMessage('encrypted',
                                     protocol=MIMEWrapper._encrypted_type)
        out.preamble = MIMEWrapper._encryption_preamble

        first_part = MIMEApplication(_data='Version: 1',
                                     _subtype=MIMEWrapper._encryption_subtype,
                                     _encoder=encode_7or8bit)
        first_part.add_header('Content-Description',
                              'PGP/MIME version identification')

        second_part = MIMEApplication(_data=str(payload),
                                      _subtype='octet-stream',
                                      _encoder=encode_7or8bit,
                                      name='encrypted.asc')
        second_part.add_header('Content-Description',
                               'OpenPGP encrypted message')
        second_part.add_header('Content-Disposition', 'inline',
                               filename='encrypted.asc')
        out.attach(first_part)
        out.attach(second_part)
        return out

    def encrypt(self, *keys, cipher=SymmetricKeyAlgorithm.AES256):
        """
        Encrypt the message with key/s, using cipher.

        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param cipher: The symmetric cipher to use.
        :type cipher: SymmetricKeyAlgorithm
        :return: The encrypted message.
        :rtype: mailman.email.message.Message
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        payload = self.msg.as_string()
        pmsg = PGPMessage.new(payload)
        pmsg = self._encrypt(pmsg, *keys, cipher=cipher)
        out = self._wrap_encrypted(pmsg)
        copy_headers(self.msg, out)
        return out

    def sign_encrypt(self, key, *keys, hash=None,
                     cipher=SymmetricKeyAlgorithm.AES256):
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
        :return: The signed + encrypted message.
        :rtype: mailman.email.message.Message
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        payload = self.msg.as_string()
        pmsg = PGPMessage.new(payload)
        pmsg |= key.sign(pmsg, hash=hash)
        pmsg = self._encrypt(pmsg, *keys, cipher=cipher)
        out = self._wrap_encrypted(pmsg)
        copy_headers(self.msg, out)
        return out

    def sign_then_encrypt(self, key, *keys, hash=None,
                          cipher=SymmetricKeyAlgorithm.AES256):
        """
        Sign then encrypt the message.

        This is as per RFC 3156 section 6.1 - RFC 1847 Encapsulation.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :param keys: The key/s to encrypt with.
        :type keys: pgpy.PGPKey
        :param hash:
        :type hash: pgpy.constants.HashAlgorithm
        :param cipher:
        :type cipher: pgpy.constants.SymmetricKeyAlgorithm
        :return: The signed + encrypted message.
        :rtype: mailman.email.message.Message
        """
        if len(keys) == 0:
            raise ValueError('At least one key necessary.')

        out = self.sign(key, hash)
        out_wrapped = MIMEWrapper(out)
        return out_wrapped.encrypt(*keys, cipher=cipher)
