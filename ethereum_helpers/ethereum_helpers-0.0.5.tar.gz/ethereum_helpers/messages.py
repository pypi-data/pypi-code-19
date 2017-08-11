import hmac
from hashlib import sha256
from typing import (Callable,
                    Tuple)

from ecdsa import SECP256k1

from .coding import (encode_number,
                     decode_number,
                     hex_string_to_int)
from .coordinates import affine
from .coordinates.utils import modular_multiplicative_inverse
from .hashes import keccak_256_hash
from .restrictions import (R_LENGTH,
                           S_LENGTH)
from .types import AffinePointType

secp256k_generator_point = SECP256k1.generator
secp256k_generator_point = (secp256k_generator_point.x(),
                            secp256k_generator_point.y())


def sign_message(message: str,
                 *,
                 signing_key_hex_string: str) -> str:
    message_hash = hash_message(message)
    v, r, s = signature_triplet(message_hash=message_hash,
                                signing_key_hex_string=signing_key_hex_string)
    return hex(r)[2:].zfill(R_LENGTH) + hex(s)[2:].zfill(S_LENGTH) + hex(v)[2:]


def add_prefix(message: str) -> str:
    # more info at
    # https://github.com/ethereum/go-ethereum/commit/b59c8399fbe42390a3d41e945d03b1f21c1a9b8d
    return ("\x19Ethereum Signed Message:\n"
            + str(len(message))
            + message)


def hash_message(message: str,
                 *,
                 message_modifier: Callable[[str], str] = add_prefix,
                 encoding: str = 'utf-8') -> str:
    modified_message = message_modifier(message)
    encoded_message = modified_message.encode(encoding)
    return keccak_256_hash(encoded_message).hexdigest()


def signature_triplet(
        *,
        message_hash: str,
        signing_key_hex_string: str,
        generator_point: AffinePointType = secp256k_generator_point,
        order: int = SECP256k1.order) -> Tuple[int, int, int]:
    message_hash_int = hex_string_to_int(message_hash)
    signing_key_int = hex_string_to_int(signing_key_hex_string)

    k = deterministic_generate_k(message_hash=message_hash,
                                 signing_key_hex_string=signing_key_hex_string)
    r, y = affine.multiply(point=generator_point,
                           multiplier=k)
    s = (modular_multiplicative_inverse(k, order)
         * (message_hash_int + r * signing_key_int) % order)
    v = 27 + ((y % 2) ^ (0 if s * 2 < order else 1))
    s = s if s * 2 < order else order - s
    return v, r, s


def deterministic_generate_k(*,
                             message_hash: str,
                             signing_key_hex_string: str) -> int:
    signing_key_int = hex_string_to_int(signing_key_hex_string)
    message_hash_int = hex_string_to_int(message_hash)
    signing_key_bytes = encode_number(signing_key_int,
                                      base=256,
                                      min_length=32)
    message_hash_bytes = encode_number(message_hash_int,
                                       base=256,
                                       min_length=32)

    v = b'\x01' * 32
    key = b'\x00' * 32
    key = hmac.new(key=key,
                   msg=v + b'\x00' + signing_key_bytes + message_hash_bytes,
                   digestmod=sha256).digest()
    v = hmac.new(key=key,
                 msg=v,
                 digestmod=sha256).digest()
    key = hmac.new(key=key,
                   msg=v + b'\x01' + signing_key_bytes + message_hash_bytes,
                   digestmod=sha256).digest()
    v = hmac.new(key=key,
                 msg=v,
                 digestmod=sha256).digest()
    return decode_number(hmac.new(key=key,
                                  msg=v,
                                  digestmod=sha256).digest(),
                         base=256)
