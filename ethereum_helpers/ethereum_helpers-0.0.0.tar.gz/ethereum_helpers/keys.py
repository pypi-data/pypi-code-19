from functools import partial
from hashlib import sha3_256
from typing import (Union,
                    Type)

from ecdsa import (SECP256k1,
                   SigningKey,
                   VerifyingKey)

from .hashes import keccak_256_hash


def hex_bytes_to_key(key_cls: Union[Type[SigningKey],
                                    Type[VerifyingKey]],
                     hex_bytes: bytes,
                     *,
                     curve=SECP256k1,
                     hash_function=sha3_256) -> SigningKey:
    return key_cls.from_string(hex_bytes,
                               curve=curve,
                               hashfunc=hash_function)


hex_bytes_to_signing_key = partial(hex_bytes_to_key,
                                   SigningKey)
hex_bytes_to_verifying_key = partial(hex_bytes_to_key,
                                     VerifyingKey)


def signing_key_to_address(key: SigningKey) -> str:
    # based on
    # https://www.reddit.com/r/ethereum/comments/69qfkv/python_script_that_converts_ethereum_private_key/
    verifying_key = key.get_verifying_key()
    return verifying_key_to_address(verifying_key)


def verifying_key_to_address(key: VerifyingKey) -> str:
    key_string = key.to_string()
    key_hash = keccak_256_hash(key_string)
    key_hash_hex = key_hash.hexdigest()
    return key_hash_hex[24:]
