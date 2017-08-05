from ecdsa import (SigningKey,
                   VerifyingKey)

from .hashes import keccak_256_hash


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
