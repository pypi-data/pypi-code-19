from featuretools.primitives import AggregationFeature, TransformFeature, DirectFeature, IdentityFeature
from featuretools.primitives import Mean, Mode, Count
from featuretools.variable_types import Discrete, Categorical


class DFSFilterBase(object):
    filter_type = 'post_instance'
    apply_to = [AggregationFeature, TransformFeature, DirectFeature]

    def apply_filter(self, f, e):
        raise NotImplementedError(self.__class__.__name__ + '.apply_filter')

    def post_instance_validate(self, f, e, target_entity_id):
        """
        Args:
            f (`.FeatureBase`): feature
            e (`.BaseEntity`): entity
            target_entity_id (str): id of target entity
        return True if this filter doesn't apply to feature f
        """
        for at in self.apply_to:
            if isinstance(f, at):
                break
        else:
            return True

        return self.apply_filter(f, e, target_entity_id)

    def pre_instance_validate(self, feature, child_feature, child_entity, where):
        for at in self.apply_to:
            if issubclass(feature, at):
                break
        else:
            return True
        return self.apply_filter(feature, child_feature, child_entity, where)

    def is_valid(self, feature=None, entity=None,
                 target_entity_id=None, child_feature=None,
                 child_entity=None, entity_path=None, forward=None,
                 where=None):

        if self.filter_type == 'pre_instance':
            args = [feature, child_feature, child_entity, where]
            func = self.pre_instance_validate

        elif self.filter_type == 'post_instance':
            args = [feature, entity, target_entity_id]
            func = self.post_instance_validate

        elif self.filter_type == 'traversal':
            args = [entity, child_entity,
                    target_entity_id, entity_path, forward]
            func = self.apply_filter

        else:
            raise NotImplementedError("Unknown filter type: {}".
                                      format(self.filter_type))

        if type(feature) != list:
            return func(*args)

        else:
            return [func(*args) for f in feature]


class LimitWhereClausesByVariableType(DFSFilterBase):
    filter_type = 'pre_instance'

    def __init__(self, variable_types=None):
        if variable_types is None:
            self.variable_types = [Categorical]
        else:
            self.variable_types = variable_types

    def apply_filter(self, feature, child_feature, child_entity, where):
        if where is None:
            return True
        for base_feat in where.base_features:
            if base_feat.variable_type not in self.variable_types:
                return False
        return True


class LimitWhereClausesByFeatureType(DFSFilterBase):
    filter_type = 'pre_instance'

    def __init__(self, feature_types=None):
        if feature_types is None:
            self.feature_types = [Count]
        else:
            self.feature_types = feature_types

    def apply_filter(self, feature, child_feature, child_entity, where):
        if where is None:
            return True
        for feature_type in self.feature_types:
            if issubclass(feature, feature_type):
                return True
        return False


class WhereFeatsDifferentThanBaseFeats(DFSFilterBase):
    filter_type = 'pre_instance'

    def apply_filter(self, feature, child_feature, child_entity, where):
        if where is None:
            return True
        for base_feat in where.base_features:
            if base_feat.hash() == child_feature.hash():
                return False
        return True


class WhereStack(DFSFilterBase):
    """
    Don't allow too much stacking of where features
    """
    filter_type = 'pre_instance'
    apply_to = [AggregationFeature]

    def __init__(self, allowed_depth=1):
        self.allowed = allowed_depth

    def apply_filter(self, feature, child_feature, child_entity, where):
        if where is None:
            return True

        wheres = [f for f in child_feature._get_deep_dependencies()
                  if isinstance(f, AggregationFeature) and f.where is not None]
        if len(wheres) >= self.allowed:
            return False
        return True


class DFeatWhere(DFSFilterBase):
    """
    don't allow dfeats of agg_feats with where clauses
    """
    filter_type = 'pre_instance'
    apply_to = [DirectFeature]

    def apply_filter(self, feature, child_feature, child_entity, where):
        # this filter applies to features which are dfeats of agg_feats
        if not isinstance(child_feature, AggregationFeature):
            return True

        deep_base_features = [child_feature] + \
            child_feature._get_deep_dependencies()

        for feat in deep_base_features:
            if isinstance(feat, AggregationFeature) and feat.where is not None:
                return False
        return True


class TraverseUp(DFSFilterBase):
    filter_type = 'traversal'

    def __init__(self, percent_low=.0005, percent_high=.9995,
                 unique_high=50, unique_low=5):
        self.percent_low = percent_low
        self.percent_high = percent_high
        self.unique_high = unique_high
        self.unique_low = unique_low

    def apply_filter(self, parent_entity, child_entity,
                     target_entity_id, entity_path, forward):
        es = parent_entity.entityset
        if not forward:
            if (parent_entity.id == target_entity_id or
                    es.find_backward_path(parent_entity.id,
                                          target_entity_id) is None):
                return True
            path = es.find_backward_path(parent_entity.id, child_entity.id)
            r = path[0]

            percent_unique = r.child_variable.percent_unique
            count = r.child_variable.count
            if (percent_unique is None or
               count is None):
                return True

            # Traverse if high absolute number of unique
            if count > self.unique_high:
                return True

            # Don't traverse if low absolute number of unique
            if count < self.unique_low:
                return False

            # Don't traverse if not unique enough or too unique
            if (percent_unique > self.percent_high or
               percent_unique < self.percent_low):
                return False

        return True


class AggFeatStack(DFSFilterBase):
    filter_type = 'post_instance'
    """
    only allow certain agg_feats to be applied to a aggregation feature
    """
    apply_to = [AggregationFeature]

    def __init__(self, allowed=None):
        self.allowed = allowed or [Mean]

    def count_agg_feats(self, path):
        return sum([1 for f in path if isinstance(f, AggregationFeature)])

    def apply_filter(self, f, e, target_entity_id):
        if self.count_agg_feats(f.get_main_dependencies()) > 0:
            if f.function_name in [a.function_name for a in self.allowed]:
                return True
            else:
                return False

        return True


class LimitModeUniques(DFSFilterBase):
    """Heuristic to discard mode feature if child feature values
    contain too many uniques.

    An individual child feature has too many uniques if the
    ratio of uniques to count values is greater than a threshold,
    defaulted to .9.
    """
    filter_type = 'post_instance'
    apply_to = [Mode]

    def __init__(self, threshold=.9):
        self.threshold = threshold

    def apply_filter(self, f, e, target_entity_id):
        child_feature = f.base_features[0]
        if not isinstance(child_feature, IdentityFeature):
            return True

        variable = child_feature.variable
        if not isinstance(variable, Discrete):
            return True

        percent_unique = variable.percent_unique
        if percent_unique is not None and (percent_unique > self.threshold):
            return False

        return True


filter_map = {
    "TraverseUp": TraverseUp,
    "AggFeatStack": AggFeatStack,
    "LimitModeUniques": LimitModeUniques,
    "WhereFeatsDifferentThanBaseFeats": WhereFeatsDifferentThanBaseFeats,
    "LimitWhereClausesByFeatureType": LimitWhereClausesByFeatureType,
    "LimitWhereClausesByVariableType": LimitWhereClausesByVariableType,
    "DFeatWhere": DFeatWhere,
    "WhereStack": WhereStack,
}


def make_filter(name, params={}):
    return filter_map[name](**params)
