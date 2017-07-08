"""
Utility module for handling cryptographic operations.
"""

import os
import base64
from Crypto.Cipher import AES

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class CryptUtils:
    """
    Utility class containing methods for performing cryptographic operations.
    """

    def __init__(self):
        pass

    @staticmethod
    def encode_string(cipher, data, block_size, padding_string):
        """
        Encrypts supplied data string using supplied cipher and encodes it using Base64.

        :param cipher: The cipher to be used for encrypting the data.
        :param data: The data string to be encoded.
        :param block_size: Represents cipher strength.
        :param padding_string: A string to be used for padding the data to be encrypted.

        :return: The base64 encoded data string, encrypted using supplied cipher.
        :rtype: str
        """

        padding = data + (block_size - len(data) % block_size) * padding_string

        return base64.b64encode(cipher.encrypt(padding))

    @staticmethod
    def encrypt_aes(data, block_size=32):
        """
        Encrypts supplied data string using AES cipher.

        :param data: The data to be encrypted.
        :param block_size: Represents cipher strength. 16->AES-128, 24->AES-192, 32->AES-256

        :return: The AES-encrypted data string with specified cipher strength.
        :rtype: str
        """

        padding_string = '{'

        secret = os.urandom(block_size)
        cipher = AES.new(secret)

        encrypted_data = CryptUtils.encode_string(cipher, data, block_size, padding_string)

        return encrypted_data
