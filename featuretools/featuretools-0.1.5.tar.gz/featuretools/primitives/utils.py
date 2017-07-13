from .feature_base import FeatureBase


def apply_dual_op_from_feat(df, f):
    left = f.left
    right = f.right
    op = None
    other = None
    if isinstance(left, FeatureBase):
        left = df[left.get_name()]
        op = getattr(left, f._get_op())
        other = right
    if isinstance(right, FeatureBase):
        right = df[right.get_name()]
        other = right
        if op is None:
            op = getattr(right, f._get_rop())
            other = left

    assert op is not None, \
        "Need at least one feature for dual op, found 2 scalars"

    return op(other)
