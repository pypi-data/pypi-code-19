# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import os

import six
from Crypto import Random
from Crypto.Hash import SHA, SHA256, SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as CipherPKCS1_V15
from Crypto.Cipher import PKCS1_OAEP as CipherPKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5 as SignaturePKCS1_V15
from Crypto.Signature import PKCS1_PSS as SignaturePKCS1_PSS


random_generator = Random.new().read


class PublicKeyFileExists(Exception):
    pass


class RSAEncryption(object):
    CIPHER_PKCS1_NONE = 1
    CIPHER_PKCS1_V1_5 = 2
    CIPHER_PKCS1_OAEP = 3

    SIGNATURE_PKCS1_V1_5 = 5
    SIGNATURE_PKCS1_PSS = 6

    bits = 1024
    public_key = None
    private_key = None

    def __init__(self):
        super(RSAEncryption, self).__init__()

    def encrypt(self, message, public_key=None, rsa_type=CIPHER_PKCS1_NONE):
        '''
        RSA 加密
        :param message:
        :param public_key:
        :param rsa_type:
        :return:
        '''
        public_key = public_key if public_key else self._get_public_key()
        public_key_object = RSA.importKey(public_key)
        if rsa_type == self.CIPHER_PKCS1_NONE:
            random_phrase = 'M'
            encrypted_message = public_key_object.encrypt(self._to_format_for_encrypt(message), random_phrase)[0]
        elif rsa_type == self.CIPHER_PKCS1_V1_5:
            cipher = CipherPKCS1_V15.new(public_key_object)
            encrypted_message = cipher.encrypt(message)
        elif rsa_type == self.CIPHER_PKCS1_OAEP:
            cipher = CipherPKCS1_OAEP.new(public_key_object)
            encrypted_message = cipher.encrypt(message)
        else:
            raise RSAEncryption(u"unknown rsa type")
        # use base64 for save encrypted_message in database without problems with encoding
        return base64.b64encode(encrypted_message)

    def decrypt(self, encoded_encrypted_message, private_key=None, rsa_type=CIPHER_PKCS1_NONE):
        '''
        RSA 解密
        :param encoded_encrypted_message:
        :param private_key:
        :param rsa_type:
        :return:
        '''
        encrypted_message = base64.b64decode(encoded_encrypted_message)
        private_key = private_key if private_key else self._get_private_key()
        private_key_object = RSA.importKey(private_key)
        if rsa_type == self.CIPHER_PKCS1_NONE:
            decrypted_message = private_key_object.decrypt(encrypted_message)
        elif rsa_type == self.CIPHER_PKCS1_V1_5:
            cipher = CipherPKCS1_V15.new(private_key_object)
            decrypted_message = cipher.decrypt(encrypted_message, random_generator)
        elif rsa_type == self.CIPHER_PKCS1_OAEP:
            cipher = CipherPKCS1_OAEP.new(private_key_object)
            decrypted_message = cipher.decrypt(encrypted_message, random_generator)
        else:
            raise RSAEncryption(u"unknown rsa type")
        return six.text_type(decrypted_message, encoding='utf8')

    def sign(self, message,  private_key=None):
        '''
        签名: 使用自己的私钥做签名
        :param messge:
        :param private_key:
        :return:
        '''
        private_key = private_key if private_key else self._get_private_key()
        private_key_object = RSA.importKey(private_key)
        signer = SignaturePKCS1_V15.new(private_key_object)
        digest = SHA.new()
        digest.update(message)
        sign = signer.sign(digest)
        return base64.b64encode(sign)

    def verify(self, message, signature, public_key=None):
        '''
        验签: 使用对方的公钥做签名校验
        :param message:
        :param signature:
        :param public_key:
        :return:
        '''
        decoded_signature = base64.b64decode(signature)
        public_key = public_key if public_key else self._get_public_key()
        public_key_object = RSA.importKey(public_key)
        verifier = CipherPKCS1_V15.new(public_key_object)
        digest = SHA.new()
        digest.update(message)
        return verifier.verify(digest, decoded_signature)

    def generate_keys_string(self):
        '''
        产生密钥对 返回 (私钥, 公钥)
        :return:
        '''
        key = RSA.generate(self.bits, random_generator)
        private, public = key.exportKey(), key.publickey().exportKey()
        return private, public

    def generate_keys(self, base_path=None, public_key_name="public_key.pem", private_key_name="private_key.pem"):
        '''
        产生密钥对, 存储到文件中, 并返回 (私钥, 公钥)
        :param base_path:
        :param public_key_name:
        :param private_key_name:
        :return:
        '''
        if not base_path:
            raise Exception(u"base_path not empty")
        self.create_directories(base_path)
        key = RSA.generate(self.bits, random_generator)
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
    private, public = encryptor.generate_keys_string()
    print str(private)
    print str(public)


