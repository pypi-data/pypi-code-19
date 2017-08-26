# -*- coding: utf-8 -*-
from __future__ import absolute_import
import base64
import rncryptor
# from cryptography.fernet import Fernet
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography import exceptions
# from cryptography import fernet

__all__ = ["cryptor", "rncryptor", ]


# class Cryptographer(object):
#     def _get_fernet(self, password=PASSWORD):
#         return Fernet(base64.urlsafe_b64encode(PBKDF2HMAC(
#             algorithm=hashes.SHA256(),
#             length=32,
#             salt=SALT,
#             iterations=100000,
#             backend=default_backend()
#         ).derive(password)))
#
#     def encrypt(self, data, password=PASSWORD):
#         return self._get_fernet(password=password).encrypt(data)
#
#     def decrypt(self, encrypted_data, password=PASSWORD):
#         try:
#             return self._get_fernet(password=password).decrypt(encrypted_data)
#         except exceptions.InvalidSignature:
#             return ""
#         except fernet.InvalidToken:
#             return ""


class RNCryptor(rncryptor.RNCryptor):
    def encrypt(self, data, password):
        try:
            endata = super(RNCryptor, self).encrypt(data=data, password=password)
        except rncryptor.RNCryptorError:
            endata = ""
        return endata

    def decrypt(self, data, password):
        try:
            dedata = super(RNCryptor, self).decrypt(data=data, password=password)
        except rncryptor.DecryptionError:
            dedata = ""
        return dedata


# cryptor = Cryptographer()
cryptor = RNCryptor()


if __name__ == '__main__':
    raw_key = "e070903a51a43d3ebd7abf1993ae6f4cc65f50c8"
    resource_key = "8a3dffd927abfa15e95c88a26ec3b64f8994ef9f"
    base64_data = "AwHC6zn3e-1NsGBNMXF1tlh76MUKcQs7oZTBpsacdVyZ5KsM7DfckV3PRh48gg-MwWpPa0Q4l_liZB0Wz6p33hN7lZTeV8OdfjyppAhxN7ND7F4FTkyC_Z6IdtBrfHHFLS_56HTUTtblTYTV58RwDF_4"

    print "raw_key   :", raw_key
    print "encrypt_data:", base64_data
    encrypt_data = base64.urlsafe_b64decode(base64_data)
    crypt_key = cryptor.decrypt(data=encrypt_data, password=resource_key)
    print "decrypt_key :", crypt_key

