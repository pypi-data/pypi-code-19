from typing import Tuple

from ecdsa import SECP256k1

from .utils import inversion

VectorType = Tuple[int, int, int]


def multiply(vector: VectorType,
             multiplier: int,
             *,
             order=SECP256k1.order) -> VectorType:
    if vector[1] == 0 or multiplier == 0:
        return 0, 0, 1
    if multiplier == 1:
        return vector
    if multiplier < 0 or multiplier >= order:
        return multiply(vector, multiplier % order)

    quotient, remainder = divmod(multiplier, 2)
    if remainder == 0:
        return double(multiply(vector, quotient))
    if remainder == 1:
        return add(double(multiply(vector,
                                   quotient)),
                   vector)


def add(vector: VectorType,
        other_vector: VectorType,
        *,
        p=SECP256k1.curve.p()) -> VectorType:
    """
    Bernstein-Lange addition

    more info at
    https://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian.html#addition-add-2007-bl
    """
    vector_x, vector_y, vector_z = vector
    other_vector_x, other_vector_y, other_vector_z = other_vector

    if not vector_y:
        return other_vector
    if not other_vector_y:
        return vector

    u_1 = (vector_x * other_vector_z ** 2) % p
    u_2 = (other_vector_x * vector_z ** 2) % p
    s_1 = (vector_y * other_vector_z ** 3) % p
    s_2 = (other_vector_y * vector_z ** 3) % p

    if u_1 == u_2:
        if s_1 != s_2:
            return 0, 0, 1
        return double(vector)

    h = u_2 - u_1
    r = s_2 - s_1
    h_2 = (h ** 2) % p
    j = (h * h_2) % p
    v = (u_1 * h_2) % p
    result_x = (r ** 2 - j - 2 * v) % p
    result_y = (r * (v - result_x) - s_1 * j) % p
    result_z = (h * vector_z * other_vector_z) % p
    return result_x, result_y, result_z


def double(vector,
           *,
           a: int = SECP256k1.curve.a(),
           p: int = SECP256k1.curve.p()) -> VectorType:
    """
    Chudnovsky–Chudnovsky doubling

    more info at
    http://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian.html#doubling-dbl-1986-cc
    """
    vector_x, vector_y, vector_z = vector
    if not vector_y:
        return 0, 0, 0
    squared_vector_y = (vector_y ** 2) % p
    s = (4 * vector_x * squared_vector_y) % p
    m = (3 * vector_x ** 2 + a * vector_z ** 4) % p
    result_x = (m ** 2 - 2 * s) % p
    result_y = (m * (s - result_x) - 8 * squared_vector_y ** 2) % p
    result_z = (2 * vector_y * vector_z) % p
    return result_x, result_y, result_z


def to_affine(vector: VectorType,
              *,
              p: int = SECP256k1.curve.p()) -> Tuple[int, int]:
    vector_x, vector_y, vector_z = vector
    z = inversion(vector_z, p)
    return (vector_x * z ** 2) % p, (vector_y * z ** 3) % p
