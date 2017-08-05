from typing import Tuple

from ecdsa import SECP256k1
from ecdsa.curves import Curve

from .coding import (encode_number,
                     hex_string_to_int)
from .coordinates import jacobian
from .coordinates.utils import modular_multiplicative_inverse
from .hashes import keccak_256_hash
from .restrictions import (R_LENGTH,
                           S_LENGTH)


def verifying_key_hex_bytes(signature: str,
                            *,
                            message: str,
                            encoding: str = 'utf-8') -> bytes:
    v, r, s = decode_signature(signature)

    prepended_message = ('\x19Ethereum Signed Message:\n'
                         + str(len(message))
                         + message)
    message_hash = (keccak_256_hash(prepended_message.encode(encoding))
                    .hexdigest())
    return verifying_key_hex_bytes_from_hash(message_hash,
                                             v=v,
                                             r=r,
                                             s=s)


def verifying_key_hex_bytes_from_hash(message_hash: str,
                                      *,
                                      v: int,
                                      r: int,
                                      s: int) -> bytes:
    left, right = verifying_key_pair(message_hash,
                                     v=v,
                                     r=r,
                                     s=s)
    result = (encode_number(left,
                            base=256,
                            min_length=32)
              + encode_number(right,
                              base=256,
                              min_length=32))

    if len(result) != 64:
        err_msg = ('Invalid public key, '
                   'should have length of 64')
        raise ValueError(err_msg)

    return result


def verifying_key_pair(message_hash: str,
                       *,
                       v: int,
                       r: int,
                       s: int,
                       curve: Curve = SECP256k1) -> Tuple[int, int]:
    if not (27 <= v <= 34):
        raise ValueError(f'"v" must in range 27-34, '
                         f'but found {v}')

    curve_fp = curve.curve
    p = curve_fp.p()
    a = curve_fp.a()
    b = curve_fp.b()
    n = curve.order
    g_x = curve.generator.x()
    g_y = curve.generator.y()

    x = r
    beta = pow((x ** 3 + a * x + b) % p, (p + 1) // 4, p)
    y = beta if v % 2 ^ beta % 2 else p - beta
    z = hex_string_to_int(message_hash)
    g_z = jacobian.multiply(point=(g_x, g_y, 1),
                            multiplier=(n - z) % n)
    xy = jacobian.multiply(point=(x, y, 1),
                           multiplier=s)
    q_r = jacobian.add(g_z, xy)
    q = jacobian.multiply(point=q_r,
                          multiplier=modular_multiplicative_inverse(r, n))
    return jacobian.to_affine(q)


def decode_signature(signature: str) -> Tuple[int, int, int]:
    r = hex_string_to_int(signature[:R_LENGTH])
    s = hex_string_to_int(signature[R_LENGTH:R_LENGTH + S_LENGTH])
    v = hex_string_to_int(signature[R_LENGTH + S_LENGTH:])
    return v, r, s
