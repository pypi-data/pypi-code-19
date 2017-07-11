from featuretools import variable_types
from .transform_feature import TransformFeature
from .feature_base import FeatureBase
import numpy as np
import operator
from .utils import apply_dual_op_from_feat


class BinaryFeature(TransformFeature):
    def __init__(self, left, right):
        if isinstance(left, (FeatureBase, variable_types.Variable)):
            left = self._check_feature(left)

        if isinstance(right, (FeatureBase, variable_types.Variable)):
            right = self._check_feature(right)

        base_features = []
        base_hashes = []

        self._left_index = -1
        if isinstance(left, FeatureBase):
            self._left_index = 0
            base_features.append(left)
            base_hashes.append(left.hash())
        else:
            self._left_value = left

        self._right_index = -1
        if isinstance(right, FeatureBase):
            if right.hash() in base_hashes:
                self._right_index = self._left_index
            else:
                self._right_index = len(base_features)
                base_features.append(right)
                base_hashes.append(right.hash())
        else:
            self._right_value = right

        if self._left_index == -1 and self._right_index == -1:
            raise ValueError("one of (left, right) must be an instance,"
                             "of FeatureBase or Variable")

        super(BinaryFeature, self).__init__(*base_features)

    @property
    def left(self):
        if self._left_index > -1:
            return self.base_features[self._left_index]
        else:
            return self._left_value

    def left_str(self):
        if isinstance(self.left, FeatureBase):
            return self.left.get_name()
        else:
            return self.left

    @property
    def right(self):
        if self._right_index > -1:
            return self.base_features[self._right_index]
        else:
            return self._right_value

    def right_str(self):
        if isinstance(self.right, FeatureBase):
            return self.right.get_name()
        else:
            return self.right

    @property
    def default_value(self):
        if isinstance(self.left, FeatureBase):
            left_default_val = self.left.default_value
        else:
            left_default_val = self.left
        if isinstance(self.right, FeatureBase):
            right_default_val = self.right.default_value
        else:
            right_default_val = self.right
        if np.isnan(left_default_val) or np.isnan(right_default_val):
            return np.nan
        else:
            return getattr(operator, self._get_op())(left_default_val, right_default_val)

    def _get_name(self):
        return "%s %s %s" % (self.left_str(),
                             self.operator, self.right_str())

    def _get_op(self):
        return self._operators[self.operator]

    def _get_rop(self):
        return self._roperators[self.operator]

    def hash(self):
        if isinstance(self.left, FeatureBase):
            left_hash = self.left.hash()
        else:
            left_hash = hash(self.left)
        if isinstance(self.right, FeatureBase):
            right_hash = self.right.hash()
        else:
            right_hash = hash(self.right)
        return hash(str(self.__class__) +
                    str(self.entity.id) +
                    str(self.operator) +
                    str(left_hash) +
                    str(right_hash))


class ArithmeticFeature(BinaryFeature):
    _ADD = '+'
    _SUB = '-'
    _MUL = '*'
    _DIV = '/'
    _MOD = '%'
    _operators = {
        _ADD: "__add__",
        _SUB: "__sub__",
        _MUL: "__mul__",
        _DIV: "__div__",
        _MOD: "__mod__",
    }

    _roperators = {
        _ADD: "__radd__",
        _SUB: "__rsub__",
        _MUL: "__rmul__",
        _DIV: "__rdiv__",
        _MOD: "__rmod__",
    }

    function_name = "arithmetic"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric
    operator = None

    @property
    def variable_type(self):
        if not isinstance(self.left, FeatureBase):
            return self.right.variable_type
        if not isinstance(self.right, FeatureBase):
            return self.left.variable_type
        left_vtype = self.left.variable_type
        right_vtype = self.right.variable_type
        dt = variable_types.Datetime
        td = variable_types.Timedelta
        if left_vtype == dt and right_vtype == dt:
            return variable_types.Timedelta
        elif left_vtype == dt or right_vtype == dt:
            return variable_types.Datetime
        elif left_vtype == td or right_vtype == td:
            return variable_types.Timedelta
        else:
            return variable_types.Numeric

    def get_function(self):
        return pd_binary


class Add(ArithmeticFeature):
    """Creates a transform feature that adds two features"""
    operator = ArithmeticFeature._ADD
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Timedelta, variable_types.Datetime),
                (variable_types.Datetime, variable_types.Timedelta),
                (variable_types.Timedelta, variable_types.Timedelta)]


class Subtract(ArithmeticFeature):
    """Creates a transform feature that subtracts two features"""
    operator = ArithmeticFeature._SUB
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Timedelta, variable_types.Datetime),
                (variable_types.Datetime, variable_types.Timedelta),
                (variable_types.Timedelta, variable_types.Timedelta),
                (variable_types.Datetime, variable_types.Datetime)]


class Multiply(ArithmeticFeature):
    """Creates a transform feature that multplies two features"""
    operator = ArithmeticFeature._MUL
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Timedelta, variable_types.Timedelta)]


class Divide(ArithmeticFeature):
    """Creates a transform feature that divides two features"""
    operator = ArithmeticFeature._DIV
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Timedelta, variable_types.Timedelta)]


class Mod(ArithmeticFeature):
    """Creates a transform feature that divides two features"""
    operator = ArithmeticFeature._MOD
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Timedelta, variable_types.Timedelta)]


class Negate(Subtract):
    """Creates a transform feature that negates a feature"""
    apply_to = [(variable_types.Numeric,),
                (variable_types.Timedelta,)]

    def __init__(self, f):
        super(Negate, self).__init__(0, f)

    def _get_name(self):
        return "-%s" % (self.right_str())


class Compare(BinaryFeature):
    """Compares two features using provided operator
        returns a boolean value"""
    EQ = '='
    NE = '!='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='

    _operators = {
        EQ: "__eq__",
        NE: "__ne__",
        LT: "__lt__",
        GT: "__gt__",
        LE: "__le__",
        GE: "__ge__"
    }

    _inv_operators = {
        EQ: NE,
        NE: EQ,
        LT: GE,
        GT: LE,
        LE: GT,
        GE: LT
    }

    _roperators = {
        EQ: "__eq__",
        NE: "__ne__",
        LT: "__ge__",
        GT: "__le__",
        LE: "__gt__",
        GE: "__lt__"
    }

    function_name = "compare"
    apply_to = [(variable_types.Variable,)]
    _variable_type = variable_types.Boolean

    def __init__(self, left, operator, right):
        self.operator = operator

        super(Compare, self).__init__(left, right)

    def invert(self):
        self.operator = self._inv_operators[self.operator]

    def get_function(self):
        return pd_binary


class LogicalFeature(BinaryFeature):
    _AND = 'AND'
    _OR = 'OR'
    _operators = {
        _AND: "__add__",
        _OR: "__or__",
    }

    _roperators = {
        _AND: "__rand",
        _OR: "__ror",
    }
    operator = None
    _variable_type = variable_types.Boolean
    apply_to = [(variable_types.Boolean, variable_types.Boolean),
                (variable_types.Boolean, variable_types.Numeric),
                (variable_types.Numeric, variable_types.Boolean)]


class And(LogicalFeature):
    operator = LogicalFeature._AND
    function_name = "and"

    def get_function(self):
        return lambda df, f: df[df.columns[0]] & df[df.columns[1]]


class Or(LogicalFeature):
    operator = LogicalFeature._OR
    function_name = "or"

    def get_function(self):
        return lambda df, f: df[df.columns[0]] | df[df.columns[1]]


def pd_binary(df, f):
    return apply_dual_op_from_feat(df, f).values
