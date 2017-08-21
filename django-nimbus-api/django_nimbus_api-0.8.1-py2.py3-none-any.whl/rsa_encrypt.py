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

    SIGNATURE_PKCS1_V1_5 = 5
    SIGNATURE_PKCS1_PSS = 6

    bits = 1024
    public_key = None
    private_key = None

    def __init__(self):
        super(RSAEncryption, self).__init__()

    def encrypt(self, message, public_key=None, **kwargs):
        '''
        RSA 加密
        :param message:
        :param public_key:
        :param rsa_type:
        :return:
        '''
        public_key = public_key if public_key else self._get_public_key()
        public_key_object = RSA.importKey(public_key)
        rsa_type = kwargs.get('rsa_type', self.CIPHER_PKCS1_NONE)
        if rsa_type == self.CIPHER_PKCS1_NONE:
            random_phrase = 'M'
            encrypted_message = public_key_object.encrypt(self._to_format_for_encrypt(message), random_phrase)[0]
        elif rsa_type == self.CIPHER_PKCS1_V1_5:
            cipher = CIPHER_PKCS1_V15.new(public_key_object)
            encrypted_message = cipher.encrypt(message)
        elif rsa_type == self.CIPHER_PKCS1_OAEP:
            cipher = CIPHER_PKCS1_OAEP.new(public_key_object)
            encrypted_message = cipher.encrypt(message)
        else:
            raise RSAEncryption(u"unknown rsa type")
        # use base64 for save encrypted_message in database without problems with encoding
        return base64.b64encode(encrypted_message)

    def decrypt(self, encoded_encrypted_message, private_key=None, **kwargs):
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
        rsa_type = kwargs.get('rsa_type', self.CIPHER_PKCS1_NONE)
        if rsa_type == self.CIPHER_PKCS1_NONE:
            decrypted_message = private_key_object.decrypt(encrypted_message)
        elif rsa_type == self.CIPHER_PKCS1_V1_5:
            cipher = CIPHER_PKCS1_V15.new(private_key_object)
            decrypted_message = cipher.decrypt(encrypted_message, random_generator)
        elif rsa_type == self.CIPHER_PKCS1_OAEP:
            cipher = CIPHER_PKCS1_OAEP.new(private_key_object)
            decrypted_message = cipher.decrypt(encrypted_message)
        else:
            raise RSAEncryption(u"unknown rsa type")
        return six.text_type(decrypted_message, encoding='utf8')

    def sign(self, message,  private_key=None, **kwargs):
        '''
        签名: 使用自己的私钥做签名
        :param messge:
        :param private_key:
        :return:
        '''
        private_key = private_key if private_key else self._get_private_key()
        private_key_object = RSA.importKey(private_key)
        signer = SIGNATURE_PKCS1_V15.new(private_key_object)
        digest = SHA.new()
        digest.update(message)
        sign = signer.sign(digest)
        return base64.b64encode(sign)

    def verify(self, message, signature, public_key=None, **kwargs):
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
        verifier = SIGNATURE_PKCS1_V15.new(public_key_object)
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
    pub_begin = b'-----BEGIN PUBLIC KEY-----\n'
    pub_end = b'\n-----END PUBLIC KEY-----'
    pri_begin = b'-----BEGIN RSA PRIVATE KEY-----\n'
    pri_end = b'\n-----END RSA PRIVATE KEY-----'

    pub_key = b"MIGdMA0GCSqGSIb3DQEBAQUAA4GLADCBhwKBgQDGQ0MmYpMSYUDkpHtvBxUFqAXpivJgOuYRjHc788X2CAw/NPC9k6iJYLPlqNGIFmIw1GZG/gpilcBxXNzz0kVlKY/IQOenrdNjzhvzv0alo1F5lk0rof2AVPMr0TDXPbBlXWS4EOFKAgtJR/m7LdgPcCKi1LnLV+4joG35YtuRrwIBAw=="
    pri_key = b"MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAMZDQyZikxJhQOSke28HFQWoBemK8mA65hGMdzvzxfYIDD808L2TqIlgs+Wo0YgWYjDUZkb+CmKVwHFc3PPSRWUpj8hA56et02POG/O/RqWjUXmWTSuh/YBU8yvRMNc9sGVdZLgQ4UoCC0lH+bst2A9wIqLUuctX7iOgbfli25GvAgEDAoGBAIQs127sYgxA1e3C/PSvY1karpux9urR7rZdpNKig/lastTN9dO3xbDrIpkbNlq5lss4RC9UBuxj1aDok0022Ozupgi0Rix45zQw0tgrM12QkqMkK8zZO6BS4tR8+nhRJHAG0nbSCom/zP6ohICf8mAlcJGwGafmmDA/ZXBENC47AkEA8OOWQwbg66esH3CE9DStCHgFb0MUwpuS8adXN6BAA3/ZOtb0L31h9NdIYh5TcWuuGwYJLtGWSvPARQDTkjBbuwJBANKzJO93hAzQ6WVvKopE7EH9f3DIY5mIfOb3ld4Y4sB55BhSEaZUGW2AgukUpsyA0Rzzvx3BuTMWGvxU/Wpc8J0CQQCgl7mCBJXyb8gU9a34Ix4FpVj012MsZ7dLxOTPwCqs/+YnOfgfqOv4j4WWvuJLnR68rrDJ4Q7cooAuAI0MID0nAkEAjHdt9PpYCItGQ59xsYNIK/5U9drtEQWomfpj6WXsgFFCuuFhGY1mSQBXRg3EiFXgvffUvoEmIg68qDio8ZNLEwJBAKcTaUU+nbLFKCwkd2bPfroY6GOPfy3+bi+ofOLjxLGjVseUg0GUW7QC0Ij5nJa1DoZU1I8j66m2gwdNF0gkGEE="

    print "===" * 10
    pw = "1234567890"
    # private = pri_begin + pri_key + pri_end
    # public = pub_begin + pub_key + pub_end
    print str(private)
    print str(public)

    print "==="*10
    print "raw: {}".format(pw)

    en_pw = encryptor.encrypt(pw, public, rsa_type=2)
    print "encrypt: {}".format(en_pw)
    de_pw = encryptor.decrypt(en_pw, private, rsa_type=2)
    print "decrypt: {}".format(de_pw)

    print "===" * 10
    signature = encryptor.sign(pw, private)
    print "signature: {}".format(signature)
    is_verify = encryptor.verify(pw, signature, public)
    print "is_verify: {}".format(is_verify)
    print "===" * 10

