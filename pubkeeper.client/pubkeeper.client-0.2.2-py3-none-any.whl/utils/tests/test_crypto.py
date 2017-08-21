from Crypto import Random
from Crypto.Cipher import AES
from unittest import TestCase

from pubkeeper.utils.crypto import PubCrypto


class TestPubCrypto(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.key = Random.new().read(16)
        self.crypto = PubCrypto(AES.MODE_CBC)

    def test_pad(self):
        with self.assertRaises(TypeError):
            self.crypto.pad('hello')

        ret = self.crypto.pad(b'hello')
        self.assertEqual(self.crypto.BS, len(ret))

    def test_unpad(self):
        with self.assertRaises(TypeError):
            self.crypto.unpad('hello')

        ret = self.crypto.unpad(self.crypto.pad(b'hello'))
        self.assertEqual(len(b'hello'), len(ret))

    def test_crypto(self):
        crypted = self.crypto.encrypt(self.key, b'hello')
        self.assertNotEqual(crypted,
                            self.crypto.encrypt(self.key, b'hello'))

        self.assertEqual(b'hello',
                         self.crypto.decrypt(self.key, crypted))

        with self.assertRaises(RuntimeError):
            self.crypto.decrypt(self.key, b'thisshouldfail')
