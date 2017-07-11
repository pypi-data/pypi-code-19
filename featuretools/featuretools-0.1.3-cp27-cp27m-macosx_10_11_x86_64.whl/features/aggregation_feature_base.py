from featuretools import variable_types
from feature_base import FeatureBase, IdentityFeature
import copy


class AggregationFeature(FeatureBase):
    """Feature for a parent entity that summarizes
        related instances in a child entity"""

    # these should be set by subclasses
    function_name = None
    _variable_type = None
    apply_to = []
    require_time_index = False
    only_id_variable = False
    allow_where = True
    stack_on_exclude = []

    def __init__(self, base_feature, parent_entity, use_previous=None,
                 where=None):
        if not hasattr(base_feature, '__iter__'):
            base_features = [self._check_feature(base_feature)]
        else:
            base_features = [self._check_feature(bf) for bf in base_feature]
            msg = "all base features must share the same entity"
            assert len(set([bf.entity for bf in base_features])) == 1, msg

        if where is not None:
            where = self._check_feature(where)

        # add support for wheres in apply_to signatures
        self.apply_to = self._apply_to_include_wheres
        self.child_entity = base_features[0].entity

        self.base_features = base_features[:]
        # only the base features used for aggregation
        self.agg_base_features = base_features[:]

        # position of the time_index within self.base_features
        self._time_index = -1
        if self.require_time_index:
            assert self.child_entity.has_time_index(), "Child entity '%s' " \
                "does not contain a time index" % (self.child_entity.id)
            time_var = IdentityFeature(self.child_entity[self.child_entity.time_index])
            base_hashes = [f.hash() for f in self.base_features]
            if time_var.hash() not in base_hashes:
                self._time_index = len(self.base_features)
                self.base_features.append(time_var)
            else:
                self._time_index = base_hashes.index(time_var.hash())

        self._add_where(where)
        self.use_previous = use_previous
        super(AggregationFeature, self).__init__(parent_entity,
                                                 self.base_features)

    @property
    def base_feature_sig(self):
        sig = self.agg_base_features[:]
        if self.time_index_feature:
            sig.append(self.time_index_feature)
        if self.where:
            sig.append(self.where)
        return sig

    @property
    def time_index_feature(self):
        if self._time_index > -1:
            return self.base_features[self._time_index]
        return None

    @property
    def _apply_to_include_wheres(self):
        return self.apply_to + [tuple(list(sig) + [variable_types.Boolean])
                                for sig in self.apply_to]

    def can_apply(self, entity, prediction_entity_id, filters=None):
        if not self._check_feature_signature():
            return False

        if self.require_time_index and not self.child_entity.has_time_index():
            return False

        # TODO: if agg feature has more than one base_feature, and
        # wants to have the others be id_variables too,
        # then we need to change the following
        base_feature = self.agg_base_features[0]

        # only apply to id variable
        if self.only_id_variable and \
            (not isinstance(base_feature, IdentityFeature) or
                base_feature.variable.id != self.child_entity.id_variable):
            return False
        # apply to anything but id variable
        elif (not self.only_id_variable and
              isinstance(base_feature, IdentityFeature) and
              base_feature.variable.id == self.child_entity.id_variable):
            return False

        if self.require_time_index:
            if self.time_index_feature.variable_type not in (variable_types.Datetime,
                                                             variable_types.Numeric):
                return False

        if not self._check_heuristics():
            return False

        if not self._apply_filters(filters, entity, prediction_entity_id):
            return False

        if self.where is not None:
            where_features = self.where.base_features
            for wbase_feat in where_features:
                if wbase_feat.hash() in self.base_hashes:
                    return False

        return True

    def get_main_dependencies(self):
        child = self.base_features[0]
        deps = [child]
        while not isinstance(child, IdentityFeature):
            child = child.base_features[0]
            deps.append(child)
        return deps

    def _where_str(self):
        if self.where is not None:
            where_str = " WHERE " + self.where.get_name()
        else:
            where_str = ''
        return where_str

    def _use_prev_str(self):
        if self.use_previous is not None:
            use_prev_str = ", Last {}".format(self.use_previous.get_name())
        else:
            use_prev_str = ''
        return use_prev_str

    def _base_feature_str(self):
        return ', ' \
            .join([bf.get_name() for bf in self.agg_base_features])

    def _get_name(self):
        where_str = self._where_str()
        use_prev_str = self._use_prev_str()

        if self.only_id_variable:
            return "%s(%s%s%s)" % (self.function_name.upper(),
                                   self.child_entity.name,
                                   where_str, use_prev_str)

        base_features_str = self._base_feature_str()

        return "%s(%s.%s%s%s)" % (self._get_func_name(),
                                  self.child_entity.name,
                                  base_features_str,
                                  where_str, use_prev_str)

    def _get_func_name(self):
        return self.function_name.upper()

    def _apply_filters(self, filters, entity, prediction_entity_id):
        if not filters:
            return True
        for f in filters:
            if not f.is_valid(self, entity=entity,
                              prediction_entity_id=prediction_entity_id):
                return False
        return True

    def _check_heuristics(self):
        max_depth_heuristic = self._max_depth_heuristic()
        if not max_depth_heuristic:
            return False

        # if either base_of heuristic is True (child feature
        # says that it can be a base for current agg
        # feature defined by cls)
        # or stack_on heuristic is True (current agg
        # feature defined by cls says that it can stack on
        # child feature)
        # then return True
        if not self._base_of_heuristic() and not self._stack_on_heuristic():
            return False
        return True

    def _max_depth_heuristic(self):
        if self.max_stack_depth:
            depth = 1
            stack = copy.copy(self.base_features)
            seen = set()
            while len(stack) > 0:
                child = stack.pop(0)
                if child.hash() in seen:
                    continue
                seen.add(child.hash())
                if isinstance(child, AggregationFeature):
                    depth += 1
                if depth > self.max_stack_depth:
                    return False
                grandchildren = []
                if not isinstance(child, IdentityFeature):
                    grandchildren = child.base_features
                for grandchild in grandchildren:
                    if grandchild.hash() not in seen:
                        stack.insert(0, grandchild)
        return True

    def _stack_on_heuristic(self):
        stack_on = self.stack_on
        stacks_on_self = self.stacks_on_self

        base_function_names = [bf.function_name for bf in self.base_features]

        if stack_on is not None:
            stack_on = copy.copy(stack_on)
            if stacks_on_self:
                stack_on.append(self.function_name)
        # stack_on is None but stacks_on_self is False
        # means that we allow stacking on everything
        # except self
        elif not stacks_on_self and self.function_name in base_function_names:
            return False
        else:
            return True

        deps = self._get_deep_dependencies()
        aggs = [d for d in deps if isinstance(d, AggregationFeature)]
        for f in aggs:
            if f.function_name not in stack_on:
                return False
        return True

    def _base_of_heuristic(self):
        for base_feature in self.base_features:
            if ((self.where is not None and base_feature.hash() == self.where.hash()) or
                (self.require_time_index and
                    base_feature.hash() == self.time_index_feature.hash())):
                continue
            base_of = base_feature.base_of
            stacks_on_self = base_feature.stacks_on_self

            if base_of is not None:
                base_of = copy.copy(base_of)
                if stacks_on_self:
                    base_of.append(base_feature.function_name)
                if self.function_name not in base_of:
                    return False
        return True
