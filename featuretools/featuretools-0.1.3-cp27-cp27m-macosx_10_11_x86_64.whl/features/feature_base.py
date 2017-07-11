from numpy import nan
from featuretools.core.base import FTBase
import copy
from featuretools.variable_types.variable import Variable, Boolean
from featuretools.entityset import Entity
from featuretools.utils.wrangle import _check_timedelta, _check_time_against_column
import pdb


import logging
logger = logging.getLogger('featuretools.scheduler')


class FeatureBase(FTBase):
    """
    Base class for all features.

    Feature attributes include:

        - get_function(): returns backend function to compute this feature
        - function_name (str): Name of backend function used to compute this feature
        - base_of (list[:class:`.FeatureBase`]): deprecated
        - stack_on (list[:class:`.FeatureBase`]): list of feature types this feature is allowed to
            have as its base feature (only relevant to AggregationFeatures)
        - stacks_on_self (bool): If True, allow this feature to have another feature of same type
            as its base feature (only relevant to AggregationFeatures)
        - max_stack_depth (int): Maximum number of features in the largest chain proceeding downward
            from this feature's base features.
        - allow_where (bool): If True, allow where clauses
        - where (:class:`.FeatureBase`): Feature to condition this feature by in computation (e.g.
            take the Count of products where the product_id is "basketball".)
        - default_value: Default value this feature returns if no data found
        - apply_to (list[tuple[:class:.`Variable`]]): list of possible variable types this feature can
            be applied to. Each element in the list represent the variable types of the base features,
            excluding any wheres. Typically these are either a single value, or two values with the second
            indicating this feature needs to be applied with a feature acting as a time index as well (see:
            :class:.`AvgTimeBetween`)
        - variable_type (:class:.`Variable`, or None): Variable type of computed feature (None if depends on
            base_features)
        - expanding (bool): If True, feature will expand into multiple values during calculation
        - requires_training (bool): If True, feature requires additional training before calculation.
            An appropriate training module should be provided to the computational backend, whose
            name matches the function's "function_name" attribute
        - require_time_index (bool): True if feature requires its associated entity to have a time index
        - requires_current_time (bool): True if feature needs to know what the current calculation time is (provided to computational
            backend as "time_last")
        - use_previous (str or :class:.`Timedelta`): Use only some amount of previous data from each time point during calculation
    """
    base_of = None
    stack_on = None
    stacks_on_self = None
    max_stack_depth = None
    allow_where = False
    where = None
    default_value = nan
    apply_to = None
    _variable_type = None
    expanding = False
    requires_training = False
    require_time_index = False
    requires_current_time = False
    use_previous = None
    _name = None
    rolling_function = False

    def __init__(self, entity, base_features, **kwargs):
        assert all(isinstance(f, FeatureBase) for f in base_features), \
            "All base features must be features"
        msg = "Duplicate base features ({}): {}".format(self.__class__, base_features)
        assert len(set([bf.hash() for bf in base_features])) == len(base_features), msg

        self.entity_id = entity.id
        self.entityset = entity.entityset
        if self.use_previous:
            self.use_previous = _check_timedelta(self.use_previous)
            assert len(self.base_features) > 0
            time_index = self.base_features[0].entity.time_index
            time_col = self.base_features[0].entity[time_index]
            assert time_index is not None,\
                "Use previous can only be defined on entities with a time index"
            assert _check_time_against_column(self.use_previous, time_col)
        self.base_features = base_features
        # variable type can be declared or inferred from first base feature
        self.additional_attributes = kwargs
        super(FeatureBase, self).__init__(**kwargs)

    @property
    def entity(self):
        return self.entityset[self.entity_id]

    @property
    def variable_type(self):
        if self._variable_type is None:
            return self.base_features[0].variable_type
        return self._variable_type

    @property
    def base_hashes(self):
        return [f.hash() for f in self.base_features]

    @property
    def base_feature_sig(self):
        """
        Provides all the base_features in terms of the feature's signature
        This means that duplicate base_features (which would be left out in self.base_features)
        should be listed here

        Subclasses should override this if base_features can be duplicated
        """
        return self.base_features

    def normalize(self, normalizer, normalized_base_features={}):
        normed = normalizer(self.entityset)
        d = copy.copy(self.__dict__)
        d['entityset'] = self.entityset.id
        base_features = d.pop('base_features')
        new_base_features = []
        for f in base_features:
            if f.hash() not in normalized_base_features:
                normalized_base_features[f.hash()] = f.normalize(normalizer, normalized_base_features)
            f = normalized_base_features[f.hash()]
            new_base_features.append(f)
        d = {k: normalizer(v) for k, v in d.iteritems()}
        d['base_features'] = new_base_features
        d['entityset'] = normed
        return d

    @property
    def where(self):
        if not self.allow_where:
            return None
        elif self._where_index > -1:
            return self.base_features[self._where_index]
        return None

    @where.setter
    def where(self, where_feat):
        self._add_where(where_feat)

    def _add_where(self, where):
        if not self.allow_where:
            return
        self._where_index = -1
        if where:
            assert where.variable_type == Boolean, \
                "where parameter must be a feature with a Boolean value"

            base_hashes = [f.hash() for f in self.base_features]
            if where.hash() not in base_hashes:
                self._where_index = len(self.base_features)
                self.base_features.append(where)
            else:
                self._where_index = base_hashes.index(where.hash())

    def head(self, n=10, time_last=None):
        """See values for feature

        Args:
            n (int) : number of instances to return

        Returns:
            :class:`pd.DataFrame` : Pandas DataFrame
        """
        from featuretools.computational_backends import calculate_feature_matrix
        cfm = calculate_feature_matrix([self], time_last=time_last).head(n)
        return cfm

    def sample(self, n=10, time_last=None):
        from featuretools.computational_backends import calculate_feature_matrix
        cfm = calculate_feature_matrix([self], time_last=time_last).sample(n)
        return cfm

    def _check_feature(self, feature):
        if isinstance(feature, Variable):
            return IdentityFeature(feature)
        elif isinstance(feature, FeatureBase):
            return feature
        if feature is None:
            pdb.set_trace()
        raise Exception("Not a feature")

    def __repr__(self):
        return "<Feature: %s>" % (self.get_name())

    def hash(self):
        return hash(self.get_name() + self.entity.id)

    def __hash__(self):
        # logger.warning("To hash a feature, use feature.hash()")
        return self.hash()

    def __eq__(self, other):
        return self.EQ(other)

    def __ne__(self, other):
        return self.NE(other)

    def __gt__(self, other):
        return self.GT(other)

    def __ge__(self, other):
        return self.GE(other)

    def __lt__(self, other):
        return self.LT(other)

    def __le__(self, other):
        return self.LE(other)

    def __add__(self, other):
        return self.ADD(other)

    def __radd__(self, other):
        from binary_transform import Add
        return Add(other, self)

    def __sub__(self, other):
        return self.SUB(other)

    def __rsub__(self, other):
        from binary_transform import Subtract
        return Subtract(other, self)

    def __div__(self, other):
        return self.DIV(other)

    def __truediv__(self, other):
        return self.DIV(other)

    def __rtruediv__(self, other):
        from binary_transform import Divide
        return Divide(other, self)

    def __rdiv__(self, other):
        from binary_transform import Divide
        return Divide(other, self)

    def __mul__(self, other):
        return self.MUL(other)

    def __rmul__(self, other):
        from binary_transform import Multiply
        return Multiply(other, self)

    def __mod__(self, other):
        return self.MOD(other)

    def __and__(self, other):
        return self.AND(other)

    def __rand__(self, other):
        from binary_transform import And
        return And(other, self)

    def __or__(self, other):
        return self.OR(other)

    def __ror__(self, other):
        from binary_transform import Or
        return Or(other, self)

    def __not__(self, other):
        return self.NOT(other)

    def __abs__(self):
        from .transform_feature import Absolute
        return Absolute(self)

    def __neg__(self):
        from .binary_transform import Negate
        return Negate(self)

    def EQ(self, other_feature_or_val):
        """Compares to other_feature_or_val by equality

        See also:
            :meth:`FeatureBase.equal_to`
        """
        from binary_transform import Compare
        return Compare(self, "=", other_feature_or_val)

    def equal_to(self, other_feature_or_val):
        """Compares to  other_feature_or_val by equality

        See also:
            :meth:`FeatureBase.EQ`
        """
        return self.EQ(other_feature_or_val)

    def NE(self, other_feature_or_val):
        """Compares to other_feature_or_val by non-equality

        See also:
            :meth:`FeatureBase.not_equal_to`
        """
        from binary_transform import Compare
        return Compare(self, "!=", other_feature_or_val)

    def not_equal_to(self, other_feature_or_val):
        """Compares to other_feature_or_val by non-equality

        See also:
            :meth:`FeatureBase.NE`
        """
        return self.NE(other_feature_or_val)

    def LT(self, other_feature_or_val):
        """Compares if less than other_feature_or_val

        See also:
            :meth:`FeatureBase.less_than`
        """
        from binary_transform import Compare
        return Compare(self, "<", other_feature_or_val)

    def less_than(self, other_feature_or_val):
        """Compares if less than other_feature_or_val

        See also:
            :meth:`FeatureBase.LT`
        """
        return self.LT(other_feature_or_val)

    def GT(self, other_feature_or_val):
        """Compares if greater than other_feature_or_val

        See also:
            :meth:`FeatureBase.GT`
        """
        from binary_transform import Compare
        return Compare(self, ">", other_feature_or_val)

    def greater_than(self, other_feature_or_val):
        """Compares if greater than other_feature_or_val

        See also:
            :meth:`FeatureBase.GT`
        """
        return self.GT(other_feature_or_val)

    def LE(self, other_feature_or_val):
        """Compares if less than or equal to other_feature_or_val

        See also:
            :meth:`FeatureBase.less_than_equal_to`
        """
        from binary_transform import Compare
        return Compare(self, "<=", other_feature_or_val)

    def less_than_equal_to(self, other_feature_or_val):
        """Compares if less than or equal to other_feature_or_val

        See also:
            :meth:`FeatureBase.LT`
        """
        return self.LE(other_feature_or_val)

    def GE(self, other_feature_or_val):
        """Compares if greater than or equal to other_feature_or_val

        See also:
            :meth:`FeatureBase.greater_than_equal_to`
        """
        from binary_transform import Compare
        return Compare(self, ">=", other_feature_or_val)

    def greater_than_equal_to(self, other_feature_or_val):
        """Compares if greater than or equal to other_feature_or_val

        See also:
            :meth:`FeatureBase.GE`
        """
        return self.GE(other_feature_or_val)

    def ADD(self, other_feature_or_val):
        """Add other_feature_or_val"""
        from binary_transform import Add
        return Add(self, other_feature_or_val)

    def add(self, other_feature_or_val):
        """Add other_feature_or_val"""
        from binary_transform import Add
        return Add(self, other_feature_or_val)

    def SUB(self, other_feature_or_val):
        """Subtract other_feature_or_val

        See also:
            :meth:`FeatureBase.subtract`
        """
        from binary_transform import Subtract
        return Subtract(self, other_feature_or_val)

    def subtract(self, other_feature_or_val):
        """Subtract other_feature_or_val

        See also:
            :meth:`FeatureBase.SUB`
        """
        return self.SUB(other_feature_or_val)

    def MUL(self, other_feature_or_val):
        """Multiply by other_feature_or_val

        See also:
            :meth:`FeatureBase.multiply`
        """
        from binary_transform import Multiply
        return Multiply(self, other_feature_or_val)

    def multiply(self, other_feature_or_val):
        """Multiply by other_feature_or_val

        See also:
            :meth:`FeatureBase.MUL`
        """
        return self.MUL(other_feature_or_val)

    def DIV(self, other_feature_or_val):
        """Divide by other_feature_or_val

        See also:
            :meth:`FeatureBase.divide`
        """
        from binary_transform import Divide
        return Divide(self, other_feature_or_val)

    def divide(self, other_feature_or_val):
        """Divide by other_feature_or_val

        See also:
            :meth:`FeatureBase.DIV`
        """
        return self.DIV(other_feature_or_val)

    def MOD(self, other_feature_or_val):
        """Take modulus of other_feature_or_val

        See also:
            :meth:`FeatureBase.modulo`
        """
        from binary_transform import Mod
        return Mod(self, other_feature_or_val)

    def modulo(self, other_feature_or_val):
        """Take modulus of other_feature_or_val

        See also:
            :meth:`FeatureBase.MOD`
        """
        return self.MOD(other_feature_or_val)

    def AND(self, other_feature):
        """Logical AND with other_feature"""
        from binary_transform import And
        return And(self, other_feature)

    def OR(self, other_feature):
        """Logical OR with other_feature"""
        from binary_transform import Or
        return Or(self, other_feature)

    def NOT(self):
        """Creates inverse of feature"""
        from transform_feature import Not
        from binary_transform import Compare
        if isinstance(self, Compare):
            return self.invert()
        return Not(self)

    def LIKE(self, like_string, case_sensitive=False):
        from transform_feature import Like
        return Like(self, like_string,
                    case_sensitive=case_sensitive)

    def isin(self, list_of_output):
        from transform_feature import IsIn
        return IsIn(self, list_of_output)

    def is_null(self):
        """Compares feature to null by equality"""
        from transform_feature import IsNull
        return IsNull(self)

    def __invert__(self):
        return self.NOT()

    def rename(self, name):
        """Rename Feature, returns copy"""
        feature_copy = copy.deepcopy(self)
        feature_copy._name = name
        return feature_copy

    def set_name(self, name):
        """.set_name() is deprecrated and will be removed, use .rename() instead"""
        print ".set_name(name) is deprecated and will be removed, use .rename(name) instead"
        return self.rename(name)

    def get_name(self):
        if self._name is not None:
            return self._name
        else:
            return self._get_name()

    def get_function(self):
        raise NotImplementedError("Implement in subclass")

    def is_link_var(self):
        if not isinstance(self, IdentityFeature):
            return False
        all_link_vars = self.entity.get_all_link_vars()
        if self.variable.id in all_link_vars:
            return True
        return False

    def _get_deep_dependencies(self):
        deps = []
        seen = set()
        queue = copy.copy(self.base_features)
        while len(queue) > 0:
            child = queue.pop(0)
            if child.hash() in seen:
                continue
            seen.add(child.hash())
            deps.insert(0, child)
            grandchildren = []
            if not isinstance(child, IdentityFeature):
                grandchildren = child.base_features
            for grandchild in grandchildren:
                if grandchild.hash() not in seen:
                    queue.append(grandchild)
        return deps

    def _get_depth(self):
        import aggregation_feature_base
        import direct_feature
        # get all paths of f in a tree
        # find highest number of directfeats and aggfeats along a single path
        num_at_level = 0
        if isinstance(self, (direct_feature.DirectFeature,
                             aggregation_feature_base.AggregationFeature)):
            num_at_level = 1
        level = [(self, num_at_level)]
        new_level = level
        while len(new_level) > 0:
            new_level = []
            for f, num_at_level in level:
                for bf in f.base_features:
                    if isinstance(bf, (direct_feature.DirectFeature,
                                       aggregation_feature_base.AggregationFeature)):
                        new_level.append((bf, num_at_level + 1))
                    else:
                        new_level.append((bf, num_at_level))
            if len(new_level) > 0:
                level = new_level
        max_num_d_agg_feats = max((l[1] for l in level))
        return max_num_d_agg_feats

    def _includes_nonzero_hlevel(self):
        import aggregation_feature_base
        import direct_feature
        base_features = copy.copy(self.base_features)
        while len(base_features) > 0:
            base_feat = base_features.pop(0)
            new_base_features = base_feat.base_features
            for bf in new_base_features:
                if (isinstance(base_feat, direct_feature.DirectFeature) and
                        isinstance(bf, aggregation_feature_base.AggregationFeature)):
                    return True
                elif not isinstance(base_feat, IdentityFeature):
                    base_features.append(bf)
        return False

    def _check_feature_signature(self):
        if self.apply_to is None:
            return True
        for _signature in self.apply_to:
            if len(self.base_feature_sig) != len(_signature):
                continue
            if all((_signature[i] == f.variable_type
                    for i, f in enumerate(self.base_feature_sig))):
                return True
        return False


class IdentityFeature(FeatureBase):
    """Feature for entity that is equivalent to underlying varaible"""
    def __init__(self, variable, name=None):
        # TODO: perhaps we can change the attributes of this class to
        # just entityset reference to original variable object
        self.variable = variable
        self._variable_type = type(variable)
        self._name = name
        self.base_feature = None
        super(IdentityFeature, self).__init__(variable.entity, [])

    def _get_name(self):
        return self.variable.id


class Feature(FeatureBase):
    """
    Alias for IdentityFeature and DirectFeature depending on arguments
    """
    def __new__(self, feature_or_var, entity=None):
        import direct_feature

        if entity is None:
            assert isinstance(feature_or_var, (Variable))
            return IdentityFeature(feature_or_var)

        assert isinstance(feature_or_var, (Variable, FeatureBase))
        assert isinstance(entity, Entity)

        if feature_or_var.entity.id == entity.id:
            return IdentityFeature(entity)

        return direct_feature.DirectFeature(feature_or_var, entity)
