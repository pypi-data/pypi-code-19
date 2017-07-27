# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function
from future.utils import python_2_unicode_compatible

import base64
import hashlib
from six import string_types, binary_type
from Crypto.Cipher import AES

from django.conf import settings
from django.utils import crypto

_cipher = None


@python_2_unicode_compatible
class AESCipher(object):
    '''
    from http://qiita.com/teitei_tk/items/0b8bae99a8700452b718
    $ python -c "import string, random; print(''.join(
       [random.choice(string.ascii_letters + string.digits) for i in range(50)]))"
    '''
    def __init__(self, key, block_size=32):
        self.bs = block_size
        key = key.encode('UTF-8', errors='replace')
        if len(key) >= block_size:
            self.key = key[:block_size]
        else:
            self.key = self._pad(key)
        self.key_hash = crypto.pbkdf2(key, key[:10], 10000, 0)
        if len(self.key_hash) < AES.block_size:
            self.key_hash += b'0' * (AES.block_size - len(self.key_hash))

    def encrypt(self, raw):
        encoded = b'0'
        if isinstance(raw, string_types):
            raw = raw.encode('UTF-8', errors='replace')
            encoded = b'1'
        if not isinstance(raw, binary_type):
            raw = repr(raw).encode('UTF-8', errors='replace')
            encoded = b'2'
        raw = self._pad(raw)
        iv = hashlib.sha1(raw).hexdigest()[:3].encode('UTF-8') + encoded
        first_block = self.key_hash[:(AES.block_size - len(iv))] + iv
        cipher = AES.new(self.key, AES.MODE_CBC, first_block)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        try:
            enc = base64.b64decode(enc)
        except (UnicodeEncodeError, TypeError):
            raise ValueError()
        iv = enc[:4]
        first_block = self.key_hash[:(AES.block_size - len(iv))] + iv
        cipher = AES.new(self.key, AES.MODE_CBC, first_block)
        raw = self._unpad(cipher.decrypt(enc[4:]))
        try:
            key = iv.decode('UTF-8')[-1]
        except UnicodeDecodeError:
            raise ValueError()
        if key == '1':
            raw = raw.decode('UTF-8', errors='replace')
        elif key == '2':
            raw = eval(raw)
        return raw

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode('UTF-8')

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


def __get_cipher():

    global _cipher
    if _cipher is None:
        _cipher = AESCipher(settings.CRYPTO_KEY)
    return _cipher


def aes_encrypt(value):
    return __get_cipher().encrypt(value)


def aes_decrypt(value):
    return __get_cipher().decrypt(value)
