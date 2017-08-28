# -*- coding: utf-8 -*-
from __future__ import absolute_import
import base64
import os

import six
from Crypto import Random
from Crypto.Hash import SHA, SHA256, SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as CIPHER_PKCS1_V15
from Crypto.Cipher import PKCS1_OAEP as CIPHER_PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5 as SIGNATURE_PKCS1_V15
from Crypto.Signature import PKCS1_PSS as SIGNATURE_PKCS1_PSS


random_generator = Random.new().read


class PublicKeyFileExists(Exception):
    pass


class RSAEncryption(object):
    CIPHER_PKCS1_NONE = 1
    CIPHER_PKCS1_V1_5 = 2
    CIPHER_PKCS1_OAEP = 3

    SIGNATURE_PKCS1_V1_5 = 1
    SIGNATURE_PKCS1_PSS = 2

    bits = 1024
    public_key = None
    private_key = None

    def __init__(self):
        super(RSAEncryption, self).__init__()

    def encrypt_big(self, message, public_key=None, sep=u'\n', passphrase=None, **kwargs):
        length = self.bits/8 - 11
        res = []
        for i in range(0, len(message), length):
            data = message[i:i+length]
            endata = self.encrypt(data, public_key, passphrase, **kwargs)
            res.append(endata)
        return sep.join(res)

    def decrypt_big(self, encoded_encrypted_message, private_key=None, sep=None, passphrase=None, **kwargs):
        res = []
        lines = encoded_encrypted_message.split(sep)
        for l in lines:
            data = self.decrypt(l, private_key, passphrase, **kwargs)
            res.append(data)
        return u"".join(res)

    def encrypt(self, message, public_key=None, passphrase=None, **kwargs):
        '''
        RSA 加密
        :param message:
        :param public_key:
        :param passphrase:
        :param cipher_type: 1, 2, 3 default: 1
        :param base64_key: True, False default: False
        :param base64_data: True, False default: True
        :return:
        '''
        cipher_type = kwargs.get('cipher_type', self.CIPHER_PKCS1_NONE)
        base64_key = kwargs.get('base64_key', False)
        base64_data = kwargs.get('base64_data', True)
        public_key = base64.standard_b64decode(public_key) if base64_key else public_key
        public_key_object = RSA.importKey(public_key, passphrase=passphrase)

        if cipher_type == self.CIPHER_PKCS1_NONE:
            random_phrase = 'M'
            encrypted_message = public_key_object.encrypt(self._to_format_for_encrypt(message), random_phrase)[0]
        elif cipher_type == self.CIPHER_PKCS1_V1_5:
            cipher = CIPHER_PKCS1_V15.new(public_key_object)
            encrypted_message = cipher.encrypt(message)
        elif cipher_type == self.CIPHER_PKCS1_OAEP:
            cipher = CIPHER_PKCS1_OAEP.new(public_key_object)
            encrypted_message = cipher.encrypt(message)
        else:
            raise RSAEncryption(u"unknown cipher type")
        # use base64 for save encrypted_message in database without problems with encoding
        return base64.b64encode(encrypted_message) if base64_data else encrypted_message

    def decrypt(self, encoded_encrypted_message, private_key=None, passphrase=None, **kwargs):
        '''
        RSA 解密
        :param encoded_encrypted_message:
        :param private_key:
        :param passphrase:
        :param cipher_type: 1, 2, 3 default: 1
        :param base64_key: True, False default: False
        :param base64_data: True, False default: True
        :return:
        '''
        cipher_type = kwargs.get('cipher_type', self.CIPHER_PKCS1_NONE)
        base64_key = kwargs.get('base64_key', False)
        base64_data = kwargs.get('base64_data', True)
        encrypted_message = base64.b64decode(encoded_encrypted_message) if base64_data else encoded_encrypted_message
        private_key = base64.standard_b64decode(private_key) if base64_key else private_key
        private_key_object = RSA.importKey(private_key, passphrase=passphrase)
        if cipher_type == self.CIPHER_PKCS1_NONE:
            decrypted_message = private_key_object.decrypt(encrypted_message)
        elif cipher_type == self.CIPHER_PKCS1_V1_5:
            cipher = CIPHER_PKCS1_V15.new(private_key_object)
            decrypted_message = cipher.decrypt(encrypted_message, random_generator)
        elif cipher_type == self.CIPHER_PKCS1_OAEP:
            cipher = CIPHER_PKCS1_OAEP.new(private_key_object)
            decrypted_message = cipher.decrypt(encrypted_message)
        else:
            raise RSAEncryption(u"unknown cipher type")
        return six.text_type(decrypted_message, encoding='utf8')

    def sign(self, message,  private_key=None, passphrase=None, **kwargs):
        '''
        签名: 使用自己的私钥做签名
        :param messge:
        :param private_key:
        :param passphrase:
        :param signature_type: 1, 2 default: 1
        :param base64_key: True, False default: False
        :param base64_signature: True, False default: True
        :return:
        '''
        base64_key = kwargs.get('base64_key', False)
        base64_signature = kwargs.get('base64_signature', True)
        private_key = base64.standard_b64decode(private_key) if base64_key else private_key
        private_key_object = RSA.importKey(private_key, passphrase=passphrase)
        signature_type = kwargs.get('signature_type', self.SIGNATURE_PKCS1_V1_5)
        if signature_type == self.SIGNATURE_PKCS1_V1_5:
            signer = SIGNATURE_PKCS1_V15.new(private_key_object)
        elif signature_type == self.SIGNATURE_PKCS1_PSS:
            signer = SIGNATURE_PKCS1_PSS.new(private_key_object)
        else:
            raise RSAEncryption(u"unknown signature type")
        digest = SHA.new()
        digest.update(message)
        sign = signer.sign(digest)
        return base64.b64encode(sign) if base64_signature else sign

    def verify(self, message, signature, public_key=None, passphrase=None, **kwargs):
        '''
        验签: 使用对方的公钥做签名校验
        :param message:
        :param signature:
        :param public_key:
        :param passphrase:
        :param signature_type: 1, 2 default: 1
        :param base64_key: True, False default: False
        :param base64_signature: True, False default: True
        :return:
        '''
        base64_key = kwargs.get('base64_key', False)
        base64_signature = kwargs.get('base64_signature', True)
        decoded_signature = base64.b64decode(signature) if base64_signature else signature
        public_key = base64.standard_b64decode(public_key) if base64_key else public_key
        public_key_object = RSA.importKey(public_key, passphrase=passphrase)
        signature_type = kwargs.get('signature_type', self.SIGNATURE_PKCS1_V1_5)
        if signature_type == self.SIGNATURE_PKCS1_V1_5:
            verifier = SIGNATURE_PKCS1_V15.new(public_key_object)
        elif signature_type == self.SIGNATURE_PKCS1_PSS:
            verifier = SIGNATURE_PKCS1_PSS.new(public_key_object)
        else:
            raise RSAEncryption(u"unknown signature type")
        digest = SHA.new()
        digest.update(message)
        return verifier.verify(digest, decoded_signature)

    def generate_keys_string(self, bits=1024, format='PEM', passphrase=None, pkcs=1, base64_key=False):
        '''
        产生密钥对 返回 (私钥, 公钥)
        :param bits: Key length, or size (in bits) of the RSA modulus. It must be a multiple of 256, and no smaller than 1024.
        :param format:
        :param passphrase:
        :param pkcs: 1, 8
        :param base64_key: True, False
        :return:
        '''
        self.bits = bits
        key = RSA.generate(bits, random_generator)
        private = key.exportKey(format=format, passphrase=passphrase, pkcs=pkcs)
        public = key.publickey().exportKey(format=format, pkcs=pkcs)
        if base64_key:
            return base64.standard_b64encode(private), base64.standard_b64encode(public)
        return private, public

    def generate_keys(self,
                      bits=1024,
                      base_path=None,
                      public_key_name="public_key.pem",
                      private_key_name="private_key.pem"):
        '''
        产生密钥对, 存储到文件中, 并返回 (私钥, 公钥)
        :param bits: Key length, or size (in bits) of the RSA modulus. It must be a multiple of 256, and no smaller than 1024.
        :param base_path:
        :param public_key_name:
        :param private_key_name:
        :return:
        '''
        self.bits = bits
        if not base_path:
            raise Exception(u"base_path not empty")
        self.create_directories(base_path)
        key = RSA.generate(bits, random_generator)
        private, public = key.exportKey(), key.publickey().exportKey()
        public_key_path = os.path.abspath(os.path.join(self.base_path, public_key_name))
        private_key_path = os.path.abspath(os.path.join(self.base_path, private_key_name))
        if os.path.isfile(public_key_path) or os.path.isfile(private_key_path):
            raise PublicKeyFileExists(u'密钥文件已存在,请删除')
        with open(private_key_path, 'w') as private_file:
            private_file.write(private)
        with open(public_key_path, 'w') as public_file:
            public_file.write(public)
        self.private_key = private
        self.public_key = public
        return private, public

    def create_directories(self, base_path=None):
        if base_path and not os.path.exists(base_path):
            os.makedirs(base_path)

    def _get_public_key(self):
        """run generate_keys() before get keys """
        return self.public_key

    def _get_private_key(self):
        """run generate_keys() before get keys """
        return self.private_key

    def _to_format_for_encrypt(self, value):
        if isinstance(value, int):
            return six.binary_type(value)
        for str_type in six.string_types:
            if isinstance(value, str_type):
                return value.encode('utf8')
        if isinstance(value, six.binary_type):
            return value


encryptor = RSAEncryption()


if __name__ == '__main__':
    bits = 1024
    base64_key = False
    passphrase = "1234567890987654321"
    private, public = encryptor.generate_keys_string(bits=bits,
                                                     format="PEM",
                                                     passphrase=passphrase,
                                                     base64_key=base64_key)

    print "===" * 10
    print "private: {}".format(private)
    print "public : {}".format(public)

    print "===" * 10
    pw = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    print "raw: {}".format(pw)
    en_pw = encryptor.encrypt_big(pw, public, passphrase=passphrase, cipher_type=2, base64_key=base64_key)
    print "encrypt: {}".format(en_pw)
    de_pw = encryptor.decrypt_big(en_pw, private, passphrase=passphrase, cipher_type=2, base64_key=base64_key)
    print "decrypt: {}".format(de_pw)

    print "===" * 10
    msg = "1234567890abcdefg"
    msg = pw
    print "message: {}".format(msg)
    signature = encryptor.sign(msg, private, passphrase=passphrase, signature_type=1, base64_key=base64_key)
    print "signature: {}".format(signature)
    is_verify = encryptor.verify(msg, signature, public, passphrase=passphrase, signature_type=1, base64_key=base64_key)
    print "is_verify: {}".format(is_verify)
    print "===" * 10

