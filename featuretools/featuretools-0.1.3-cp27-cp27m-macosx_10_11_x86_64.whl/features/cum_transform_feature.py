from .transform_feature import TransformFeature
from featuretools.variable_types.variable import Discrete
from .aggregation_features import Sum, Mean, Count, Max, Min
from featuretools.entityset import Timedelta
import pandas as pd
import numpy as np
from .utils import apply_dual_op_from_feat


class CumFeature(TransformFeature):
    allow_where = True
    agg_feature = None
    rolling_function = True

    # Note: Any row with a nan value in the group by feature will have a
    # NaN value in the cumfeat

    # Todo: also passing the parent entity instead of the group_feat
    def __init__(self, base_feature, group_feature,
                 where=None, use_previous=None, *args, **kwargs):
        """Summary

        Args:
            agg_feature (type): subclass of :class:`.AggregationFeature`;
                aggregation method being used.  This is passed by the
                constructors of the cumfeat subclasses
            base_feature (:class:`.FeatureBase` or :class:`.Variable`): Feature
                or variable calculated on
            group_feature (:class:`.FeatureBase` or :class:`.Variable`): Feature
                or variable used to group the rows before computation
            where (optional[:class:`.FeatureBase`]):
            use_previous (optional[:class:`.Timedelta`):
        """
        self.function_name = self.agg_feature.function_name
        self.apply_to = self.agg_feature.apply_to
        self._variable_type = self.agg_feature.variable_type

        self.use_previous = use_previous
        base_feature = self._check_feature(base_feature)
        self.base_features = [base_feature]

        group_feature = self._check_feature(group_feature)
        assert issubclass(group_feature.variable_type, Discrete), \
            "group_feature must have a discrete variable_type"
        if group_feature.hash() not in self.base_hashes:
            self.base_features.append(group_feature)
        self.group_feature = group_feature

        self._add_where(where)

        args = self.base_features + list(args)
        super(CumFeature, self).__init__(*args, **kwargs)

    def _get_name(self):
        where_str = ""
        use_prev_str = ""

        if self.where is not None:
            where_str = " WHERE " + self.where.get_name()

        if self.use_previous is not None:
            use_prev_str = ", Last %s" % (self.use_previous.get_name())

        base_features_str = "%s GROUPED BY %s" % \
            (self.base_features[0].get_name(), self.group_feature.get_name())

        return "%s(%s%s%s)" % (self.function_name.upper(), base_features_str,
                               where_str, use_prev_str)

    @property
    def base_feature_sig(self):
        sig = self.base_features[:]
        sig_hash = [s.hash() for s in sig]
        if self.group_feature and self.group_feature.hash() not in sig_hash:
            sig.append(self.group_feature)
            sig_hash.append(self.group_feature.hash())
        if self.where and self.where.hash() not in sig_hash:
            sig.append(self.where)
            sig_hash.append(self.where.hash())
        return sig

    def get_function(self):
        rolling_func = self.function_name

        def pd_rolling(df, f):
            assert f.use_previous is None or f.use_previous.unit == Timedelta._Observations
            bf_name = f.base_features[0].get_name()
            groupby = f.group_feature.get_name()

            if f.use_previous and not f.where:
                def apply_rolling(group):
                    rolled = group[bf_name].rolling(window=f.use_previous.value,
                                                    min_periods=1)
                    return getattr(rolled, rolling_func)()
            elif not f.where:
                cumfuncs = {"count": "cumcount",
                            "sum": "cumsum",
                            "max": "cummax",
                            "min": "cummin",
                            "prod": "cumprod",
                            }
                if rolling_func in ["count", "sum", "max", "min"]:
                    cumfunc = cumfuncs[rolling_func]
                    grouped = df.groupby(groupby, sort=False)[bf_name]
                    applied = getattr(grouped, cumfunc)()
                    # TODO: to produce same functionality as the rolling cases already
                    # implemented, we add 1
                    # We may want to consider changing this functionality to instead
                    # return count of the *previous* events
                    if rolling_func == "count":
                        applied += 1
                    return applied
                else:
                    def apply_rolling(group):
                        rolled = group[bf_name].expanding(min_periods=1)
                        return getattr(rolled, rolling_func)()
            elif f.use_previous and f.where:
                def apply_rolling(group):
                    mask = apply_dual_op_from_feat(group, f.where)
                    output = pd.Series(np.nan, index=group.index)
                    rolled = group[mask][bf_name].rolling(window=f.use_previous.value,
                                                          min_periods=1)
                    rolled = getattr(rolled, rolling_func)()
                    output[mask] = rolled
                    return output
            elif f.where:
                def apply_rolling(group):
                    mask = apply_dual_op_from_feat(group, f.where)
                    output = pd.Series(np.nan, index=group.index)
                    rolled = group[mask][bf_name].expanding(min_periods=1)
                    rolled = getattr(rolled, rolling_func)()
                    output[mask] = rolled
                    return output

            grouped_df = df.groupby(groupby).apply(apply_rolling)
            grouped_df.reset_index(level=0, drop=True, inplace=True)

            if isinstance(grouped_df, pd.DataFrame):
                return grouped_df.stack(dropna=False).values

            return grouped_df.values
        return pd_rolling


class CumSum(CumFeature):
    """
    Calculates the sum of previous values of an instance for each value in a time-dependent entity.
    """
    default_value = 0
    agg_feature = Sum


class CumMean(CumFeature):
    """
    Calculates the mean of previous values of an instance for each value in a time-dependent entity.
    """
    default_value = 0
    agg_feature = Mean


class CumCount(CumFeature):
    """
    Calculates the number of previous values of an instance for each value in a time-dependent entity.
    """
    default_value = 0
    agg_feature = Count


class CumMax(CumFeature):
    """
    Calculates the max of previous values of an instance for each value in a time-dependent entity.
    """
    default_value = 0
    agg_feature = Max


class CumMin(CumFeature):
    """
    Calculates the min of previous values of an instance for each value in a time-dependent entity.
    """
    default_value = 0
    agg_feature = Min
