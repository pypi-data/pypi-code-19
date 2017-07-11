from .feature_base import FeatureBase, IdentityFeature
from featuretools.variable_types.variable import Discrete
from featuretools import variable_types
import datetime
import numpy as np
import os
import pandas as pd
from pandas.core.common import is_timedelta64_dtype
current_path = os.path.dirname(os.path.realpath(__file__))
FEATURE_DATASETS = os.path.join(os.path.join(current_path, '..'), 'feature_datasets')


class TransformFeature(FeatureBase):
    """Feature for entity that is a based off one or more other features
        in that entity"""

    function_name = None
    _variable_type = None
    apply_to = []
    use_previous = None

    def __init__(self, *base_features):
        self.base_features = [self._check_feature(f) for f in base_features]
        if any(bf.expanding for bf in self.base_features):
            self.expanding = True
        assert len(set([f.entity for f in self.base_features])) == 1, \
            "More than one entity for base features"
        super(TransformFeature, self).__init__(self.base_features[0].entity,
                                               self.base_features)

    def can_apply(self, entity):
        if not self._check_feature_signature():
            return False

        for base_feature in self.base_features:
            if (isinstance(base_feature, IdentityFeature) and
                    base_feature.variable.id == entity.id_variable):
                return False

        return True

    def _get_name(self):
        name = "{}(".format(self.function_name.upper())
        name += ", ".join(f.get_name() for f in self.base_features)
        name += ")"
        return name

    @property
    def default_value(self):
        return self.base_features[0].default_value


class Day(TransformFeature):
    """Transform Datetime feature into the day (0 - 30) of the month,
       or Timedelta features into number of days they encompass"""
    function_name = "day"
    apply_to = [(variable_types.Datetime,),
                (variable_types.Timedelta,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return pd_time_unit("day")


class Hour(TransformFeature):
    """Transform Datetime feature into the hour (0 - 23) of the day,
       or Timedelta features into number of hours they encompass"""
    function_name = "hour"
    apply_to = [(variable_types.Datetime,),
                (variable_types.Timedelta,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return pd_time_unit("hour")


class Minute(TransformFeature):
    """Transform Datetime feature into the minute (0 - 59) of the hour,
       or Timedelta features into number of minutes they encompass"""
    function_name = "minute"
    apply_to = [(variable_types.Datetime,),
                (variable_types.Timedelta,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return pd_time_unit("minute")


class Month(TransformFeature):
    """Transform Datetime feature into the month (0 - 11) of the year,
       or Timedelta features into number of months they encompass """
    function_name = "month"
    apply_to = [(variable_types.Datetime,),
                (variable_types.Timedelta,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return pd_time_unit("month")


class Year(TransformFeature):
    """Transform Datetime feature into the year,
       or Timedelta features into number of years they encompass"""
    function_name = "year"
    apply_to = [(variable_types.Datetime,),
                (variable_types.Timedelta,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return pd_time_unit("year")


class Weekend(TransformFeature):
    """Transform Datetime feature into the boolean of Weekend"""
    function_name = "is_weekend"
    apply_to = [(variable_types.Datetime,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return lambda df, f: pd_time_unit("weekday")(df, f) > 4


class Weekday(TransformFeature):
    """Transform Datetime feature into the day (0 - 6) of the Week"""
    function_name = "weekday"
    apply_to = [(variable_types.Datetime,)]
    _variable_type = variable_types.Ordinal

    def get_function(self):
        return pd_time_unit("weekday")


# TODO: not implemented yet
class Percentile(TransformFeature):
    function_name = "percentile"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


class Absolute(TransformFeature):
    """Absolute value of base feature"""
    function_name = "absolute"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric

    def get_function(self):
        return lambda df, f: df[df.columns[0]].abs()


class Like(TransformFeature):
    """Equivalent to SQL LIKE(%text%)
       Returns true if text is contained with the string base_feature
    """
    function_name = "like"
    apply_to = [(variable_types.Text,), (variable_types.Categorical,)]
    _variable_type = variable_types.Boolean

    def __init__(self, base_feature, like_statement, case_sensitive=False):
        self.like_statement = like_statement
        self.case_sensitive = case_sensitive
        super(Like, self).__init__(base_feature)

    def get_function(self):
        def pd_like(df, f):
            return df[df.columns[0]].str.contains(f.like_statement,
                                                  case=f.case_sensitive)
        return pd_like


class IsNull(TransformFeature):
    """For each value of base feature, return true if value is null"""
    function_name = "is_null"
    apply_to = [(variable_types.Boolean,), (variable_types.Categorical,),
                (variable_types.Ordinal,), (variable_types.Numeric,),
                (variable_types.Datetime,), (variable_types.Text,)]
    _variable_type = variable_types.Boolean

    def get_function(self):
        return lambda df, f: df[df.columns[0]].isnull()


class TimeSince(TransformFeature):
    """
    For each value of the base feature, compute the timedelta between it and a datetime
    """
    function_name = "time_since"
    apply_to = [(variable_types.Datetime,)]
    _variable_type = variable_types.Numeric
    requires_current_time = True

    def __init__(self, base_feature, time=None):
        if time is not None:
            assert isinstance(time, datetime.datetime), 'time not type datetime'
        self.time = time
        super(TimeSince, self).__init__(base_feature)

    def get_function(self):
        def pd_time_since(df, f):
            time = f.time
            if time is None:
                time = datetime.now()
            # TODO: check if this is the same, and replace
            # time_diff = time - df[df.columns[0]]
            # return pd_time_unit('day')(time_diff, f)
            return df[df.columns[0]].apply(lambda x, days_in_seconds=86400:
                                           (time - x).total_seconds() / days_in_seconds)
        return pd_time_since


class IsIn(TransformFeature):
    """
    For each value of the base feature, checks whether it is in a list that is provided.
    """
    function_name = "isin"
    apply_to = [(variable_types.Categorical,)]
    _variable_type = variable_types.Boolean

    def __init__(self, base_feature, list_of_outputs):
        self.list_of_outputs = list_of_outputs
        super(IsIn, self).__init__(base_feature)

    def get_function(self):
        def pd_is_in(df, f):
            return df[df.columns[0]].isin(f.list_of_outputs)
        return pd_is_in

    def _get_name(self):
        return "%s.isin(%s)" % (self.base_features[0].get_name(), str(self.list_of_outputs))


class Diff(TransformFeature):
    """
    For each value of the base feature, compute the difference between it and the previous value
    """
    function_name = "diff"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric

    def __init__(self, base_feature, group_feature=None):
        """Summary

        Args:
            base_feature (:class:`FeatureBase`): base feature
            group_feature (None, optional): variable or feature to group
                rows by before calculating diff

        """
        if group_feature is not None:
            group_feature = self._check_feature(group_feature)
            assert issubclass(group_feature.variable_type, Discrete), \
                "group_feature must have a discrete variable_type"
            self.group_feature = group_feature
            super(Diff, self).__init__(base_feature, group_feature)
        else:
            self.group_feature = None
            super(Diff, self).__init__(base_feature)

    def _get_name(self):

        if self.group_feature is not None:
            base_features_str = self.base_features[0].get_name() + " GROUPED BY " + self.group_feature.get_name()
        else:
            base_features_str = self.base_features[0].get_name()
        return "%s(%s)" % (self.function_name.upper(), base_features_str)

    @property
    def base_feature_sig(self):
        sig = self.base_features[:]
        if self.group_feature and self.group_feature._get_name() not in sig:
            sig.append(self.group_feature)
        return sig

    def get_function(self):
        def pd_diff(df, f):
            if f.group_feature is not None:
                groupby = f.group_feature.get_name()
                grouped_df = df.groupby(groupby).diff()
                bf_name = f.base_features[0].get_name()
                if isinstance(df[bf_name].iloc[0], (datetime.datetime, pd.Timestamp)):
                    # TODO: check if this is the same, and replace
                    # return  pd_time_unit('day')(df[bf_name].diff(), f)
                    return grouped_df[bf_name].apply(lambda x, days_in_seconds=86400:
                                                     x.total_seconds() / days_in_seconds)
                else:
                    return grouped_df[bf_name]
            else:
                bf_name = f.base_features[0].get_name()
                if isinstance(df[bf_name].iloc[0], (datetime.datetime, pd.Timestamp)):
                    # TODO: check if this is the same, and replace
                    # return pd_time_unit('day')(df[bf_name].diff(), f)
                    return df[bf_name].diff().apply(lambda x, days_in_seconds=86400:
                                                    x.total_seconds() / days_in_seconds)
                else:
                    return df[bf_name].diff()
        return pd_diff


class Not(TransformFeature):
    function_name = "not"
    apply_to = [(variable_types.Boolean,)]
    _variable_type = variable_types.Boolean

    def _get_name(self):
        return "NOT({})".format(self.base_features[0].get_name())

    def _get_op(self):
        return "__not__"

    def get_function(self):
        return lambda df, f: ~df[df.columns[0]]


class Word2VecCluster(TransformFeature):
    """
    Uses a word vector corpus to convert words in a text feature
    into numeric vectors, and then clusters those numeric vectors
    using MiniBatchKMeans.

    base_feature must be an IdentityFeature with variable_type = Text

    Requires a corpus of word vectors. Downlaod the GoogleNews corpus from
    "https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit"
    and place it into feature_datasets/corpus.
    """
    function_name = "word2vec"
    apply_to = [(variable_types.Text,)]
    _variable_type = variable_types.Numeric
    requires_training = True
    expanding = True

    corpus_locations = {
        "google_news": ("GoogleNews-vectors-negative300.bin.gz",
                        "https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit")
    }

    def __init__(self, base_feature, num_clusters=20, normalize=False,
                 corpus="google_news",
                 obey_time_bounds_in_training=False,
                 unknown_misspelled_word="skip",
                 cluster_max_iter=100,
                 cluster_max_no_improvement=10,
                 cluster_tol=0.0,
                 cluster_batch_size=100,
                 cluster_n_init=3,
                 cluster_reassignment_ratio=0.01,
                 random_state=1):
        if isinstance(base_feature, FeatureBase) and not isinstance(base_feature, IdentityFeature):
            raise ValueError("Word2Vec feature can only be applied to textual IdentityFeatures")
        self.num_clusters = num_clusters
        self.cluster_max_iter = cluster_max_iter
        self.cluster_max_no_improvement = cluster_max_no_improvement
        self.cluster_tol = cluster_tol
        self.cluster_batch_size = cluster_batch_size
        self.cluster_n_init = cluster_n_init
        self.cluster_reassignment_ratio = cluster_reassignment_ratio
        self.random_state=random_state
        self._normalize = normalize

        assert corpus in self.corpus_locations,\
            "Unkown corpus: {}".format(corpus)
        self.corpus_name = corpus
        self.corpus_path = self._find_corpus_path()
        self.obey_time_bounds_in_training = obey_time_bounds_in_training
        self.unknown_misspelled_word = unknown_misspelled_word

        super(Word2VecCluster, self).__init__(base_feature)

    @property
    def default_value(self):
        return np.zeros(self.num_clusters) * np.nan

    def _get_name(self):
        # TODO: include cluster params?
        name = "Word2VecNumInCluster(num_clusters={}, corpus={}, normalized={})".format(
            self.num_clusters, self.corpus_name, self._normalize)
        return name

    def _find_corpus_path(self):
        filename, loc = self.corpus_locations[self.corpus_name]
        return os.path.join(os.path.join(FEATURE_DATASETS, "corpus"),
                            filename)

    @property
    def training_set(self):
        return self.corpus_name

    def check_downloaded_corpus(self):
        corpus_dir = os.path.join(FEATURE_DATASETS, "corpus")
        if not os.path.exists(corpus_dir):
            os.makedirs(corpus_dir)
        corpuses = os.listdir(corpus_dir)
        filename, loc = self.corpus_locations[self.corpus_name]
        if filename not in corpuses:
            raise ValueError(("{} Corpus not found, please download it from the "
                              "following link and place it in feature_datasets"
                              "/corpus: {}".format(filename, loc)))

    def get_function(self):
        def pd_word2vec(df, f, trainer):
            return trainer.calculate_features(df, f)
        return pd_word2vec


ALL_TRANS_FEATS = [Percentile, Day, Hour, Month, Year, Weekday, Weekend, Diff, TimeSince, IsIn]


def pd_time_unit(time_unit):
    def inner(df, f):
        if is_timedelta64_dtype(df.iloc[0]):
            seconds = pd.Series(pd.TimedeltaIndex(df[df.columns[0]]).total_seconds())
            seconds = seconds.values
            if time_unit == 'second':
                return seconds
            elif time_unit == 'minute':
                return seconds / 60
            elif time_unit == 'hour':
                return seconds / 3600
            elif time_unit == 'day':
                return seconds / (3600 * 24)
            elif time_unit == 'month':
                return seconds / (3600 * 24 * 30.42)
            elif time_unit == 'year':
                return seconds / (3600 * 24 * 365.25)
            else:
                raise ValueError("Unit {} not allowed in time unit row functions".format(time_unit))
        else:
            return getattr(pd.DatetimeIndex(df[df.columns[0]]), time_unit)
    return inner
