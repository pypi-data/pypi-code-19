from functools import partial

import scrypt
from Cryptodome.Hash import keccak


def keccak_hash(target_bytes: bytes,
                *,
                digest_bits: int) -> keccak.Keccak_Hash:
    return keccak.new(digest_bits=digest_bits,
                      data=target_bytes)


keccak_256_hash = partial(keccak_hash,
                          digest_bits=256)


def scrypt_hash(password: str,
                *,
                salt: bytes,
                n: int,
                r: int,
                p: int,
                buffer_length: int) -> bytes:
    return scrypt.hash(password,
                       salt,
                       n, r, p,
                       buffer_length)
