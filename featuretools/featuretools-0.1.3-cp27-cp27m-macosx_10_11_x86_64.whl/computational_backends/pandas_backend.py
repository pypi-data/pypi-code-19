# general
import uuid
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime


# featuretools
from .base_backend import ComputationalBackend
from .feature_tree import FeatureTree
from .word2vec_clustering import Word2VecClusterTrainer
from featuretools.entityset import Timedelta
from featuretools import variable_types
from featuretools.entityset.relationship import Relationship
from featuretools.exceptions import UnknownFeature
from featuretools.primitives import (IdentityFeature, TransformFeature,
                                   DirectFeature, AggregationFeature,
                                   apply_dual_op_from_feat)

# profiling/debugging
import logging
import pdb
import cProfile
import cStringIO
import pstats
import os
import warnings


warnings.simplefilter('ignore', np.RankWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)
logger = logging.getLogger('featuretools.computational_backend')
ROOT_DIR = os.path.expanduser("~")


class PandasBackend(ComputationalBackend):
    def __init__(self, entityset, features):
        assert len(set(f.entity.id for f in features)) == 1, \
            "Features must all be defined on the same entity"

        self.entityset = entityset
        self.target_eid = features[0].entity.id
        self.features = features

        self.feature_tree = FeatureTree(entityset, features)
        self.trained_features = self._find_trained_features()

        self.shared_training_sets = set(["google_news"])
        self.trainers = {
            'word2vec': Word2VecClusterTrainer()
        }

    def _find_trained_features(self):
        trained_features = defaultdict(list)
        ordered_entities = self.feature_tree.ordered_entities
        for eid in ordered_entities:
            for fgroup in self.feature_tree.ordered_feature_groups[eid]:
                for f in fgroup:
                    if f.requires_training:
                        trained_features[f.training_set].append(f)
        return trained_features

    def _keep_loaded_data(self, feature):
        # Check if there is a future trained feature that
        # needs access to the same entityset
        # This flag will keep that entityset in memory
        assert feature.training_set in self.trained_features
        if feature.training_set in self.shared_training_sets:
            feature_shared_entityset = self.trained_features[feature.training_set]
            for i, f in enumerate(feature_shared_entityset):
                if i < len(feature_shared_entityset) - 1:
                    return True
        return False

    def calculate_all_features(self, instance_ids, time_last,
                               training_window=None, profile=False):
        """
        Given a list of instance ids and features with a shared time window,
        generate and return a mapping of instance -> feature values.

        Args:
            instance_ids (list): list of instance id to build features for

            time_last (pd.Timestamp): last allowed time. Data from exactly this
                time not allowed

            training_window (:class:Timedelta, optional): Data older than
                time_last by more than this will be ignored

            profile (boolean): enable profiler if True

        Returns:
            pd.DataFrame : Pandas DataFrame of calculated feature values.
                Indexed by instance_ids. Columns in same order as features
                passed in.

        """
        assert len(instance_ids) > 0, "0 instance ids provided"
        self.instance_ids = instance_ids

        self.time_last = time_last

        # For debugging
        if profile:
            pr = cProfile.Profile()
            pr.enable()

        # Access the index to get the filtered data we need
        target_entity = self.entityset[self.target_eid]
        ordered_entities = self.feature_tree.ordered_entities
        eframes_by_filter = \
            self.entityset.get_pandas_data_slice(filter_entity_ids=ordered_entities,
                                                 index_eid=self.target_eid,
                                                 instances=instance_ids,
                                                 time_last=time_last,
                                                 training_window=training_window)
        # Handle an empty time slice by returning a dataframe with defaults
        if eframes_by_filter is None:
            return self._generate_default_df(instance_ids=instance_ids,
                                             id_var=target_entity.id_variable)

        # Iterate over the top-level entities (filter entities) in sorted order
        # and calculate all relevant features under each one.
        finished_entity_ids = []
        for filter_eid in ordered_entities:
            entity_frames = eframes_by_filter[filter_eid]

            # update the current set of entity frames with the computed features
            # from previously finished entities
            for eid in finished_entity_ids:
                # only include this frame if it's not from a descendent entity:
                # descendent entity frames will have to be re-calculated.
                # TODO: this check might not be necessary, depending on our
                # constraints
                if not self.entityset.find_backward_path(start_entity_id=filter_eid,
                                                         goal_entity_id=eid):
                    entity_frames[eid] = eframes_by_filter[eid][eid]

            for group in self.feature_tree.ordered_feature_groups[filter_eid]:
                handler = self._feature_type_handler(group[0])
                handler(group, entity_frames)

            finished_entity_ids.append(filter_eid)
        # debugging
        if profile:
            pr.disable()
            s = cStringIO.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats("cumulative", "tottime")
            ps.print_stats()
            prof_folder_path = os.path.join(ROOT_DIR, 'prof')
            if not os.path.exists(prof_folder_path):
                os.mkdir(prof_folder_path)
            with open(os.path.join(prof_folder_path, 'inst-%s.log' %
                                   list(instance_ids)[0]), 'w') as f:
                f.write(s.getvalue())

        df = eframes_by_filter[self.target_eid][self.target_eid]

        # fill in empty rows with default values
        missing_ids = [i for i in instance_ids if i not in
                       df[target_entity.id_variable]]
        if missing_ids:
            df = df.append(self._generate_default_df(instance_ids=missing_ids,
                                                     id_var=target_entity.id_variable,
                                                     columns=df.columns))
        return df[[feat.get_name() for feat in self.features]]

    def _get_ignored_variables(self, features):
        deps = [d for feat in features for d in [feat] + feat._get_deep_dependencies()
                if isinstance(d, IdentityFeature)]
        entity_vars = defaultdict(list)
        for d in deps:
            if d.variable.id not in entity_vars[d.entity.id]:
                entity_vars[d.entity.id].append(d.variable.id)
        return entity_vars

    def _generate_default_df(self, instance_ids, id_var, columns=None):
        default_row = [f.default_value for f in self.features]
        default_cols = [f.get_name() for f in self.features]
        default_matrix = [default_row] * len(instance_ids)
        default_df = pd.DataFrame(default_matrix,
                                  columns=default_cols,
                                  index=instance_ids)
        if columns is not None:
            for c in columns:
                if c not in default_df.columns:
                    default_df[c] = [np.nan] * len(instance_ids)
        default_df[id_var] = instance_ids
        return default_df

    def _feature_type_handler(self, f):
        if isinstance(f, TransformFeature):
            return self._calculate_transform_features
        elif isinstance(f, DirectFeature):
            return self._calculate_direct_features
        elif isinstance(f, AggregationFeature):
            return self._calculate_agg_features
        elif isinstance(f, IdentityFeature):
            return self._calculate_identity_features
        else:
            raise UnknownFeature("{} feature unknown".format(f.__class__))

    def _calculate_identity_features(self, features, entity_frames):
        entity_id = features[0].entity.id
        assert entity_id in entity_frames and features[0].get_name() in entity_frames[entity_id].columns

    def _calculate_transform_features(self, features, entity_frames):
        entity_id = features[0].entity.id
        assert len(set([f.entity.id for f in features])) == 1, \
            "features must share base entity"
        assert entity_id in entity_frames

        frame = entity_frames[entity_id]
        for f in features:
            # handle when no data
            if frame.shape[0] == 0:
                frame[f.get_name()] = np.nan
                continue

            if f.requires_current_time and f.time is None:  # used for TimeSince
                f.time = self.time_last

            if f.requires_training:
                self._train_feature(f,
                                    keep_loaded_data=self._keep_loaded_data(f))
            # collect only the variables we need for this transformation
            variable_ids = [bf.get_name() for bf in f.base_features]

            # figure out which transform function to use on the dataframe
            if f.rolling_function:
                if f.use_previous and f.use_previous.unit != Timedelta._Observations:
                    # if this feature has a timedelta use_previous property, use a
                    # special rolling agg function

                    def feature_func(df, f):
                        return build_rolling_timedelta(df, f, f.rolling_func_name, f.entity)

                    variable_ids.extend([f.entity.time_index, f.entity.id_variable])
                else:
                    feature_func = f.get_function()
            else:
                feature_func = f.get_function()

            # apply the function to the relevant dataframe slice and add the
            # feature row to the results dataframe.
            if f.requires_training:
                trainer = self.trainers[f.function_name]
                frame[f.get_name()] = feature_func(frame[variable_ids], f,
                                                   trainer)
            else:
                values = feature_func(frame[variable_ids], f)
                if isinstance(values, pd.Series):
                    values = values.values
                frame[f.get_name()] = list(values)

        entity_frames[entity_id] = frame

    def _calculate_direct_features(self, features, entity_frames):
        entity_id = features[0].entity.id
        parent_entity_id = features[0].parent_entity.id
        assert entity_id in entity_frames and parent_entity_id in entity_frames

        # TODO: support direct features on grandparents
        path = self.entityset.find_forward_path(entity_id, parent_entity_id)
        assert len(path) == 1, \
            "Error calculating DirectFeatures, len(path) > 1"

        parent_df = entity_frames[parent_entity_id]
        child_df = entity_frames[entity_id]
        merge_var = path[0].child_variable.id

        # generate a mapping of old column names (in the parent entity) to
        # new column names (in the child entity) for the merge
        col_map = {path[0].parent_variable.id: merge_var}
        index_as_feature = None
        for f in features:
            if f.base_feature.get_name() == path[0].parent_variable.id:
                index_as_feature = f
            col_map[f.base_feature.get_name()] = f.get_name()

        # merge the identity feature from the parent entity into the child
        merge_df = parent_df[col_map.keys()].rename(columns=col_map)
        if index_as_feature is not None:
            merge_df.set_index(index_as_feature.get_name(), inplace=True, drop=False)
        else:
            merge_df.set_index(merge_var, inplace=True)
        entity_frames[entity_id] = pd.merge(left=child_df, right=merge_df,
                                            left_on=merge_var, right_index=True,
                                            how='left')

    def _calculate_agg_features(self, features, entity_frames):
        test_feature = features[0]
        use_previous = test_feature.use_previous
        base_features = test_feature.base_features
        where = test_feature.where
        entity = test_feature.entity
        child_entity = base_features[0].entity
        # print "======================="
        # print "features", features
        # print "entity", entity
        # print "test_feature", test_feature
        # print "where", test_feature.where
        # print "use_previous", use_previous
        # print "base_features", base_features
        # print "child_entity", child_entity
        # print "======================="

        assert entity.id in entity_frames and child_entity.id in entity_frames

        id_var = entity.id_variable
        frame = entity_frames[entity.id]
        base_frame = entity_frames[child_entity.id]

        # handle where clause for all functions below
        if where is not None:
            base_frame = base_frame[base_frame[where.get_name()]]

        relationship_path = self.entityset.find_backward_path(entity.id,
                                                              child_entity.id)
        groupby_var = Relationship._get_link_variable_name(relationship_path)

        # if the use_previous property exists on this feature, include only the
        # instances from the child entity included in that Timedelta
        if use_previous:
            assert child_entity.has_time_index(), (
                "Applying function that requires time index to entity that "
                "doesn't have one")

            # Filter by use_previous values
            time_last = self.time_last
            if not time_last:
                time_last = datetime.now()

            if use_previous.is_absolute():
                time_first = time_last - use_previous
                ti = child_entity.time_index
                base_frame = base_frame[base_frame[ti] >= time_first]
            else:
                n = use_previous.value

                def last_n(df):
                    return df.iloc[-n:]

                base_frame = base_frame.groupby(groupby_var).apply(last_n)

        if base_frame.empty or not frame[id_var].isin(base_frame[groupby_var]).any():
            for f in features:
                default = f.default_value
                if hasattr(default, '__iter__'):
                    l = entity_frames[entity.id].shape[0]
                    default = [f.default_value] * l

                entity_frames[entity.id][f.get_name()] = default
            return

        def wrap_func_with_name(func, name):
            def inner(x):
                return func(x)
            inner.__name__ = name
            return inner

        to_agg = {}
        agg_rename = {}
        to_apply = set()
        # apply multivariable and time-dependent features as we find them, and
        # save aggregable features for later
        for f in features:
            if _can_agg(f):
                variable_id = f.base_features[0].get_name()
                if variable_id not in to_agg:
                    to_agg[variable_id] = []
                func = f.get_function()
                if isinstance(func, basestring):
                    funcname = func
                else:
                    # make sure function names are unique
                    random_id = str(uuid.uuid1())
                    func = wrap_func_with_name(func, random_id)
                    funcname = random_id
                to_agg[variable_id].append(func)
                agg_rename["{}-{}".format(variable_id, funcname)] = f.get_name()

                continue
            if f.require_time_index:
                assert child_entity.has_time_index(), (
                    "Applying function that requires time index to entity that"
                    "doesn't have one")

            to_apply.add(f)

        # Apply the non-aggregable functions generate a new dataframe, and merge
        # it with the existing one
        if len(to_apply):
            wrap = agg_wrapper(to_apply)
            # groupby_var can be both the name of the index and a column,
            # to silence pandas warning about ambiguity we explicitly pass
            # the column (in actuality grouping by both index and group would
            # work)
            to_merge = base_frame.groupby(base_frame[groupby_var]).apply(wrap)

            to_merge.reset_index(1, drop=True, inplace=True)
            frame = pd.merge(left=frame, right=to_merge,
                             left_on=id_var, right_index=True, how='left')

        # Apply the aggregate functions to generate a new dataframe, and merge
        # it with the existing one
        # Do the [variables] accessor on to_merge because the agg call returns
        # a dataframe with columns that contain the dataframes we want
        if len(to_agg):
            # groupby_var can be both the name of the index and a column,
            # to silence pandas warning about ambiguity we explicitly pass
            # the column (in actuality grouping by both index and group would
            # work)

            to_merge = base_frame.groupby(base_frame[groupby_var]).agg(to_agg)
            # we apply multiple functions to each column, creating
            # a multiindex as the column
            # rename the columns to a concatenation of the two indexes
            to_merge.columns = ["{}-{}".format(n1, n2)
                                for n1, n2 in to_merge.columns.ravel()]
            # to enable a rename
            to_merge = to_merge.rename(columns=agg_rename)
            variables = agg_rename.values()
            to_merge = to_merge[variables]
            frame = pd.merge(left=frame, right=to_merge,
                             left_on=id_var, right_index=True, how='left')

        # Handle default values
        # 1. handle non scalar default values
        iterfeats = [f for f in features
                     if hasattr(f.default_value, '__iter__')]
        for f in iterfeats:
            nulls = pd.isnull(frame[f.get_name()])
            for ni in nulls[nulls].index:
                frame.at[ni, f.get_name()] = f.default_value

        # 2. handle scalars default values
        fillna_dict = {f.get_name(): f.default_value for f in features
                       if f not in iterfeats}
        frame.fillna(fillna_dict, inplace=True)

        # convert boolean dtypes to floats as appropriate
        # pandas behavior: https://github.com/pydata/pandas/issues/3752
        for f in features:
            if (not f.expanding and f.variable_type == variable_types.Numeric and
                    frame[f.get_name()].dtype.name in ['object', 'bool']):
                frame[f.get_name()] = frame[f.get_name()].astype(float)

        entity_frames[entity.id] = frame

    def _train_feature(self, feature, keep_loaded_data=False):
        trainer = self.trainers[feature.function_name]
        if trainer.completed_training(feature):
            return
        else:
            trainer.train(feature, self.entityset, keep_loaded_data=keep_loaded_data,
                          time_last=self.time_last)


def _can_agg(feature):
    assert isinstance(feature, AggregationFeature)
    base_features = feature.base_features
    if feature.where is not None:
        base_features = [bf.get_name() for bf in base_features
                         if bf.get_name() != feature.where.get_name()]
    return len(base_features) == 1 and not feature.expanding


def agg_wrapper(feats):
    def wrap(df):
        d = {}
        for f in feats:
            func = f.get_function()
            base_features = f.base_feature_sig
            # remove where
            variable_ids = [bf.get_name() for bf in base_features
                            if f.where is None or
                            bf.get_name() != f.where.get_name()]

            input_data = [df[v] for v in variable_ids]
            args = input_data
            if f.expanding:
                args.insert(0, f)
            d[f.get_name()] = [func(*args)]
        return pd.DataFrame(d)
    return wrap


def build_rolling_timedelta(df, f, func_name, entity):
    """
    This is a special case, because pandas has no built-in way to calculate a
    rolling window defined by a time slice. We need to manually iterate over
    the rows, figure out the rolling window for each one, and calculate the
    feature values one at a time.
    """
    groupby = f.group_feature.get_name()
    bf_name = f.base_features[0].get_name()
    timedelta = f.use_previous
    time_index = entity.time_index
    id_variable = entity.id_variable

    # this function applies a rolling math function to a grouped
    # dataframe, pretty much by hand. this is very slow. avoid.
    def apply_rolling_timedelta(group):
        timedelta.data = group[time_index]
        output = pd.Series(f.default_value, index=group.index)

        # mask out certain rows if there's a `where` clause
        if f.where:
            mask = apply_dual_op_from_feat(group, f.where)
            group = group[mask]

        group_sorted = group.set_index(time_index).sort_index()

        # we need to iterate over each row in the group individually
        for inst_time in group_sorted.index.drop_duplicates():
            # find the time of the beginning of the rolling tail,
            # relative to the time of the current instance
            start_time = inst_time - timedelta
            id_vals = group_sorted[id_variable].ix[inst_time]

            #
            rolling_tail = group_sorted.ix[start_time:inst_time][bf_name]

            # aggregate the row's tail and append it to the output
            if len(rolling_tail):
                res = getattr(rolling_tail, func_name)()
            else:
                res = f.default_value

            output[id_vals] = res

        if len(output) > len(group):
            pdb.set_trace()

        return output

    grouped_df = df.groupby(groupby).apply(apply_rolling_timedelta)
    grouped_df.reset_index(level=0, drop=True, inplace=True)

    if isinstance(grouped_df, pd.DataFrame):
        return grouped_df.stack(dropna=False).values

    return grouped_df.values
