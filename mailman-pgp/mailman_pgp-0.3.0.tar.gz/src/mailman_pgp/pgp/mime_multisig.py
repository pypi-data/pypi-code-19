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

"""MIMEWrapper with multiple signature as per draft-ietf-openpgp-multsig-02."""
import copy
from email import message_from_string
from email.encoders import encode_7or8bit
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import collapse_rfc2231_value

from mailman.email.message import Message
from pgpy import PGPSignature

from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.utils.email import copy_headers


class MIMEMultiSigWrapper(MIMEWrapper):
    """https://tools.ietf.org/html/draft-ietf-openpgp-multsig-02"""

    _signature_preamble = \
        'This is an OpepPGP/MIME signed message' \
        '(RFC 4880, 3156 and draft-ietf-openpgp-multsig).\n' \
        'see https://tools.ietf.org/html/draft-ietf-openpgp-multsig-02' \
        'for more details.'

    def is_signed(self):
        """
        Whether the message is signed as per draft-ietf-openpgp-multsig-02.

        :return: If the message is MIME signed.
        :rtype: bool
        """
        if not self._is_mime():
            return False
        second_part = self.msg.get_payload(1)
        second_type = second_part.get_content_type()
        protocol_param = collapse_rfc2231_value(self.msg.get_param('protocol',
                                                                   ''))
        content_subtype = self.msg.get_content_subtype()

        return (second_part.is_multipart() and
                second_type == 'multipart/mixed' and
                content_subtype == 'signed' and
                protocol_param == 'multipart/mixed' and
                all(part.get_content_type() == MIMEWrapper._signed_type
                    for part in second_part.get_payload()))

    def get_signature(self):
        """

        :return:
        :rtype: typing.Generator[pgpy.PGPSignature]
        """
        for part in self.msg.get_payload(1).get_payload():
            try:
                sig = PGPSignature.from_blob(part.get_payload())
            except:
                continue
            yield sig

    def strip_signature(self):
        pass

    def sign(self, key, **kwargs):
        """
        Sign a message with key.

        :param key: The key to sign with.
        :type key: pgpy.PGPKey
        :return:
        :rtype: MIMEMultiSigWrapper
        """

        if self.is_signed():
            signed = next(iter(self.get_signed()))
            signature = key.sign(signed, **kwargs)
            sig_part = MIMEApplication(_data=str(signature),
                                       _subtype=MIMEWrapper._signature_subtype,
                                       _encoder=encode_7or8bit,
                                       name='signature.asc')
            sig_part.add_header('Content-Description',
                                'OpenPGP digital signature')
            sig_part.add_header('Content-Disposition', 'attachment',
                                filename='signature.asc')
            micalg = self.msg.get_param('micalg')
            micalg += ',' + self._micalg(signature.hash_algorithm)
            self.msg.set_param('micalg', micalg)
            self.msg.get_payload(1).attach(sig_part)
        else:
            original_msg = copy.deepcopy(self.msg)
            to_sign = next(iter(self.get_payload()))
            signature = key.sign(to_sign, **kwargs)
            self.msg.set_payload([])
            self.msg.attach(original_msg)
            self.msg.set_type('multipart/signed')
            self.msg['MIME-Version'] = '1.0'
            self.msg.set_param('protocol', 'multipart/mixed')
            self.msg.set_param('micalg',
                               self._micalg(signature.hash_algorithm))
            sig_part = MIMEApplication(_data=str(signature),
                                       _subtype=MIMEWrapper._signature_subtype,
                                       _encoder=encode_7or8bit,
                                       name='signature.asc')
            sig_part.add_header('Content-Description',
                                'OpenPGP digital signature')
            sig_part.add_header('Content-Disposition', 'attachment',
                                filename='signature.asc')
            second_part = MIMEMultipart()
            second_part.attach(sig_part)
            self.msg.attach(second_part)
        self.msg.preamble = MIMEMultiSigWrapper._signature_preamble
        return self

    def verify(self, key):
        """
        Verify the signatures of this message with key.

        :param key: The key to verify with.
        :type key: pgpy.PGPKey
        :return: The verified signature.
        :rtype: Generator[pgpy.types.SignatureVerification]
        """
        clear_text = next(iter(self.get_signed()))
        for signature in self.get_signature():
            try:
                verification = key.verify(clear_text, signature)
            except:
                continue
            yield verification

    def decrypt(self, key):
        """
        Decrypt this message with key.

        :param key: The key to decrypt with.
        :type key: pgpy.PGPKey
        :return:
        :rtype: MIMEMultiSigWrapper
        """
        pmsg = next(iter(self.get_encrypted()))
        decrypted = key.decrypt(pmsg)

        dmsg = decrypted.message
        if isinstance(dmsg, bytearray):
            dmsg = dmsg.decode(decrypted.charset or 'utf-8')

        out = message_from_string(dmsg, _class=Message)
        if decrypted.is_signed:
            # result should be a multisig signed thing, so [out,  ]
            self.msg.set_payload([])
            self.msg.attach(out)
            self.msg.set_type('multipart/signed')
            self.msg['MIME-Version'] = '1.0'
            self.msg.set_param('protocol', 'multipart/mixed')
            micalg = ', '.join(self._micalg(sig.hash_algorithm)
                               for sig in decrypted.signatures)
            self.msg.set_param('micalg', micalg)
            second_part = MIMEMultipart()
            for signature in decrypted.signatures:
                sig = MIMEApplication(_data=str(signature),
                                      _subtype=MIMEWrapper._signature_subtype,
                                      _encoder=encode_7or8bit,
                                      name='signature.asc')
                sig.add_header('Content-Description',
                               'OpenPGP digital signature')
                sig.add_header('Content-Disposition', 'attachment',
                               filename='signature.asc')
                second_part.attach(sig)
            self.msg.attach(second_part)
        else:
            # result should be
            self.msg.set_payload(out.get_payload())
            copy_headers(out, self.msg, True)

        return self
