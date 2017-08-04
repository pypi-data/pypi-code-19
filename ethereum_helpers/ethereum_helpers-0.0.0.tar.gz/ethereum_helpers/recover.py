from typing import Tuple

from ecdsa import SECP256k1
from ecdsa.curves import Curve

from . import jacobian_coordinates
from .coding import (encode_number,
                     hex_string_to_int)
from .hashes import keccak_256_hash
from .utils import inversion


def verifying_key(signature: str,
                  message: str) -> bytes:
    prepended_message = ('\x19Ethereum Signed Message:\n'
                         + str(len(message))
                         + message)
    message_hash = (keccak_256_hash(prepended_message.encode('ascii'))
                    .hexdigest())
    v, r, s = decode_signature(signature)

    return verifying_key_from_hash(message_hash,
                                   v=v,
                                   r=r,
                                   s=s)


def verifying_key_from_hash(message_hash: str,
                            *,
                            v: int,
                            r: int,
                            s: int) -> bytes:
    left, right = verifying_key_pair(message_hash,
                                     v=v,
                                     r=r,
                                     s=s)
    result = (encode_number(left, 256, 32)
              + encode_number(right, 256, 32))

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
    g_z = jacobian_coordinates.multiply((g_x, g_y, 1), (n - z) % n)
    xy = jacobian_coordinates.multiply((x, y, 1), s)
    q_r = jacobian_coordinates.add(g_z, xy)
    q = jacobian_coordinates.multiply(q_r, inversion(r, n))
    return jacobian_coordinates.to_affine(q)


def decode_signature(signature: str) -> Tuple[int, int, int]:
    r = hex_string_to_int(signature[:64])
    s = hex_string_to_int(signature[64:128])
    v = hex_string_to_int(signature[128:])
    return v, r, s
