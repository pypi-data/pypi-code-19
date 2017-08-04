import hmac
from hashlib import sha256
from typing import Tuple

from ecdsa import SECP256k1

from .coding import (encode_number,
                     decode_number,
                     hex_string_to_int)
from .coordinates import affine
from .coordinates.utils import modular_multiplicative_inverse
from .hashes import keccak_256_hash
from .types import AffinePointType

secp256k_generator_point = SECP256k1.generator
secp256k_generator_point = (secp256k_generator_point.x(),
                            secp256k_generator_point.y())


def sign_message(message: str,
                 *,
                 signing_key_hex_string: str) -> str:
    """
    Signs message by signing key hex string.

    E.g.:

        from ethereum_helpers.messages import sign_message

        signing_key_hex_string = 'd6259296f278203e6e1b75f6f9e10e8a798e22a5c52b2fcfa97f9dc7877218e2'
        message = 'Hello World!'
        signature = sign_message(message,
                                 signing_key_hex_string=signing_key_hex_string)
        assert signature == '0x32f73d320caf637abe9212c2fd2baf9218e1f7f009c8b16c72932986f14fdc575ab242e7c270f5fb469ca5af70392d96ca0b43276acab4b2d6dcc4903453653a1b'
    """

    message_hash = hash_message(message)
    v, r, s = signature_triplet(message_hash=message_hash,
                                signing_key_hex_string=signing_key_hex_string)
    return hex(r)[2:] + hex(s)[2:] + hex(v)[2:]


def hash_message(message: str) -> str:
    prepended_message = ("\x19Ethereum Signed Message:\n"
                         + str(len(message))
                         + message)
    return keccak_256_hash(prepended_message.encode('ascii')).hexdigest()


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
    k = b'\x00' * 32
    k = hmac.new(k,
                 v + b'\x00' + signing_key_bytes + message_hash_bytes,
                 digestmod=sha256).digest()
    v = hmac.new(k, v,
                 digestmod=sha256).digest()
    k = hmac.new(k, v + b'\x01' + signing_key_bytes + message_hash_bytes,
                 digestmod=sha256).digest()
    v = hmac.new(k, v, sha256).digest()
    return decode_number(hmac.new(k, v,
                                  digestmod=sha256).digest(),
                         base=256)
