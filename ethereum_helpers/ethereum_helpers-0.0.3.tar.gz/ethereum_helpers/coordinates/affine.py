from typing import Tuple

from ethereum_helpers.types import JacobianPointType

from . import jacobian

AffinePointType = Tuple[int, int]


def to_jacobian(point: AffinePointType) -> JacobianPointType:
    return point[0], point[1], 1


def multiply(*,
             point: AffinePointType,
             multiplier: int) -> AffinePointType:
    return jacobian.to_affine(jacobian.multiply(point=to_jacobian(point),
                                                multiplier=multiplier))
