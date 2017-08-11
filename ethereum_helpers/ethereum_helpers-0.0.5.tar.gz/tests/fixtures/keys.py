from codecs import encode
from hashlib import sha256

import pytest
from ecdsa import (SigningKey,
                   VerifyingKey)
from ecdsa.curves import (SECP256k1,
                          Curve)
from ethereum_helpers.keys import HashFunctionType


@pytest.fixture(scope='function')
def curve() -> Curve:
    return SECP256k1


@pytest.fixture(scope='function')
def hash_function() -> HashFunctionType:
    return sha256


@pytest.fixture(scope='function')
def signing_key(curve: Curve,
                hash_function: HashFunctionType) -> SigningKey:
    return SigningKey.generate(curve=curve,
                               hashfunc=hash_function)


@pytest.fixture(scope='function')
def verifying_key(signing_key: SigningKey) -> VerifyingKey:
    return signing_key.get_verifying_key()


@pytest.fixture(scope='function')
def signing_key_hex_bytes(signing_key: SigningKey) -> bytes:
    return signing_key.to_string()


@pytest.fixture(scope='function')
def verifying_key_hex_bytes(verifying_key: VerifyingKey) -> bytes:
    return verifying_key.to_string()


@pytest.fixture(scope='function')
def signing_key_hex_string(signing_key_hex_bytes: bytes) -> bytes:
    return encode(signing_key_hex_bytes, 'hex').decode('ascii')


@pytest.fixture(scope='function')
def verifying_key_hex_string(verifying_key_hex_bytes: bytes) -> bytes:
    return encode(verifying_key_hex_bytes, 'hex').decode('ascii')
