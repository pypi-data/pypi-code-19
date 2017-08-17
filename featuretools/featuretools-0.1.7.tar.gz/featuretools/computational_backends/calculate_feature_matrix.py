import pandas as pd
from .pandas_backend import PandasBackend
from featuretools.utils.gen_utils import make_tqdm_iterator
from featuretools.primitives import PrimitiveBase, AggregationPrimitive, DirectFeature
from datetime import datetime
from collections import defaultdict
from featuretools.utils.wrangle import _check_timedelta
from pandas.tseries.frequencies import to_offset
import numpy as np
import os
from toolz import merge
from functools import wraps
import shutil
import logging
import gc
logger = logging.getLogger('featuretools.computational_backend')


def calculate_feature_matrix(features, cutoff_time=None, instance_ids=None,
                             entities=None, relationships=None, entityset=None,
                             training_window=None, approximate=None,
                             save_progress=None, verbose=False,
                             backend_verbose=False,
                             verbose_desc='calculate_feature_matrix',
                             profile=False):
    """Calculates a matrix for a given set of instance ids and calculation times.

    Args:
        features (list[:class:`.PrimitiveBase`]): Feature definitions to be calculated.

        cutoff_time (pd.DataFrame or Datetime): specifies what time to calculate
            the features for each instance at.  Can either be a DataFrame with
            'instance_id' and 'time' columns, a list of values, or a single
            value to calculate for all instances.

        instance_ids (list(ob)): if cutoff_time isn't provided, list of instance ids.

        entities (dict[str->tuple(pd.DataFrame, str, str)]): dictionary of
            entities. Entries take the format
            {entity id: (dataframe, id column, (time_column))}

        relationships (list[(str, str, str, str)]): list of relationships
            between entities. List items are a tuple with the format
            (parent entity id, parent variable, child entity id, child variable)

        entityset (:class:`.EntitySet`): An already initialized entityset. Required if
            entities and relationships are not defined

        training_window (dict[str-> :class:`Timedelta`] or :class:`Timedelta`, optional):
            Window or windows defining how much older than the cutoff time data
            can be to be included when calculating the feature.  To specify
            which entities to apply windows to, use a dictionary mapping entity
            id -> Timedelta. If None, all older data is used.

        approximate (Timedelta or str): frequency to group instances with similar
            cutoff times by for features with costly calculations. For example,
            if bucket is 24 hours, all instances with cutoff times on the same
            day will use the same calculation for expensive features.

        verbose (Optional(boolean)): Print progress info. The time granularity is per time group
            unless there is only a single cutoff time, in which case backend_verbose is turned on

        backend_verbose (Optional(boolean)): Print progress info of each feature calculatation step per time group

        profile (Optional(boolean)): Enables profiling if True

        save_progress (Optional(str)): path where to save intermediate computational results
    """
    assert (isinstance(features, list) and features != [] and
            all([isinstance(feature, PrimitiveBase) for feature in features])), \
        "features must be a non-empty list of features"

    # handle loading entityset
    from featuretools.entityset.entityset import EntitySet
    if not isinstance(entityset, EntitySet):
        if entities is not None and relationships is not None:
            entityset = EntitySet("entityset", entities, relationships)

    if entityset is not None:
        for f in features:
            f.entityset = entityset

    entityset = features[0].entityset
    target_entity = features[0].entity

    if not isinstance(cutoff_time, pd.DataFrame):
        if cutoff_time is None:
            cutoff_time = datetime.now()

        if instance_ids is None:
            index_var = target_entity.index
            instance_ids = target_entity.df[index_var].tolist()

        if not isinstance(cutoff_time, list):
            cutoff_time = [cutoff_time] * len(instance_ids)

        # TODO are these sorted correctly?
        map_args = [(id, time) for id, time in zip(instance_ids, cutoff_time)]
        df_args = pd.DataFrame(map_args, columns=['instance_id', 'time'])
        df_args.sort_values('time', inplace=True)
        to_calc = df_args.values
        cutoff_time = pd.DataFrame(to_calc, columns=['instance_id', 'time'])
    else:
        cutoff_time = cutoff_time.copy()

    # Get dictionary of features to approximate
    if approximate is not None:
        to_approximate = gather_approximate_features(features)
        ignored = {
            entity: f.hash()
            for entity, approx_features in to_approximate.items()
            for f in approx_features
        }
    else:
        to_approximate = defaultdict(list)
        ignored = None

    # Check if there are any non-approximated aggregation features
    no_unapproximated_aggs = True
    for feature in features:
        if isinstance(feature, AggregationPrimitive):
            # do not need to check if feature is in to_approximate since
            # only base features of direct features can be in to_approximate
            no_unapproximated_aggs = False
            break
        deps = feature.get_deep_dependencies(ignored=ignored)
        for dependency in deps:
            if (isinstance(dependency, AggregationPrimitive) and
                    dependency not in to_approximate[dependency.entity.id]):
                no_unapproximated_aggs = False
                break

    cutoff_df_time_var = 'time'
    target_time = '_original_time'

    if approximate is not None:
        # If there are approximated aggs, bin times
        binned_cutoff_time = bin_cutoff_times(cutoff_time.copy(), approximate)

        # Think about collisions: what if original time is a feature
        binned_cutoff_time[target_time] = cutoff_time[cutoff_df_time_var]

        grouped = binned_cutoff_time.groupby(cutoff_df_time_var, sort=True)

    else:
        grouped = cutoff_time.groupby(cutoff_df_time_var, sort=True)

    # if the backend is going to be verbose, don't make cutoff times verbose
    if verbose and not backend_verbose:
        iterator = make_tqdm_iterator(iterable=grouped,
                                      total=len(grouped),
                                      desc="Progress",
                                      unit="cutoff time")
    else:
        iterator = grouped

    feature_matrix = []
    backend = PandasBackend(entityset, features)
    for _, group in iterator:
        _feature_matrix = calculate_batch(features, group, approximate,
                                          entityset, backend_verbose,
                                          training_window, profile, verbose,
                                          save_progress, backend,
                                          no_unapproximated_aggs, cutoff_df_time_var,
                                          target_time)
        feature_matrix.append(_feature_matrix)
        # Do a manual garbage collection in case objects from calculate_batch
        # weren't collected automatically
        gc.collect()

    feature_matrix = pd.concat(feature_matrix)

    if save_progress and os.path.exists(os.path.join(save_progress, 'temp')):
        shutil.rmtree(os.path.join(save_progress, 'temp'))

    return feature_matrix


def calculate_batch(features, group, approximate, entityset, backend_verbose, training_window,
                    profile, verbose, save_progress, backend,
                    no_unapproximated_aggs, cutoff_df_time_var, target_time):
    if approximate is not None:
        precalculated_features, ignored = approximate_features(features,
                                                               group,
                                                               window=approximate,
                                                               entityset=entityset,
                                                               training_window=training_window,
                                                               verbose=backend_verbose,
                                                               profile=profile)
    else:
        precalculated_features = None
        ignored = None

    if no_unapproximated_aggs and approximate is not None:
        group[target_time] = datetime.now()

    if backend_verbose is None:
        one_cutoff_time = group[cutoff_df_time_var].nunique() == 1
        backend_verbose = verbose and one_cutoff_time

    @save_csv_decorator(save_progress)
    def calc_results(time_last, ids, precalculated_features=None, training_window=None):
        matrix = backend.calculate_all_features(ids, time_last,
                                                training_window=training_window,
                                                precalculated_features=precalculated_features,
                                                ignored=ignored,
                                                profile=profile,
                                                verbose=backend_verbose)
        return matrix

    # if approximated features, get precalculated values and set cutoff_time to unbinned time
    if precalculated_features is not None:
        group[cutoff_df_time_var] = group[target_time]

    grouped = group.groupby(cutoff_df_time_var, sort=True)

    for _, group in grouped:
        time_last = group[cutoff_df_time_var].iloc[0]
        ids = group['instance_id'].values

        if no_unapproximated_aggs and approximate is not None:
            window = None
        else:
            window = training_window

        feature_matrix = calc_results(time_last, ids, precalculated_features=precalculated_features, training_window=window)

        # this can occur when the features for an instance are calculated at
        # multiple cutoff times which were binned to the same frequency.
        if len(feature_matrix) != len(group):
            feature_matrix = pd.merge(group[['id', target_time]], feature_matrix, left_on=['id'], right_index=True)
            feature_matrix.set_index('id', inplace=True)
            feature_matrix.sort_values(target_time, inplace=True)
            feature_matrix.drop(target_time, inplace=True, axis=1)

    return feature_matrix


def bin_cutoff_times(cuttoff_time, bin_size):
    binned_cutoff_time = cuttoff_time.copy()
    if type(bin_size) == int:
        binned_cutoff_time['time'] = binned_cutoff_time['time'].apply(lambda x: x / bin_size * bin_size)
    else:
        bin_size = _check_timedelta(bin_size).get_pandas_timedelta()
        binned_cutoff_time['time'] = datetime_round(binned_cutoff_time['time'], bin_size)
    return binned_cutoff_time


def save_csv_decorator(save_progress=None):
    def inner_decorator(method):
        @wraps(method)
        def wrapped(*args, **kwargs):
            if save_progress is None:
                r = method(*args, **kwargs)
            else:
                time = args[0].to_pydatetime()
                file_name = 'ft_' + time.strftime("%Y_%m_%d_%I-%M-%S-%f") + '.csv'
                file_path = os.path.join(save_progress, file_name)
                temp_dir = os.path.join(save_progress, 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                temp_file_path = os.path.join(temp_dir, file_name)
                r = method(*args, **kwargs)
                r.to_csv(temp_file_path)
                os.rename(temp_file_path, file_path)
            return r
        return wrapped
    return inner_decorator


def approximate_features(features, cutoff_time, window, entityset,
                         training_window=None, verbose=None, profile=None):
    '''Given a list of features and cutoff_times to be passed to
    calculate_feature_matrix, calculates approximate values of some features
    to speed up calculations.  Cutoff times are sorted into
    window-sized buckets and the approximate feature values are only calculated
    at one cutoff time for each bucket.


    ..note:: this only approximates DirectFeatures of AggregationPrimitives, on
        the target entity. In future versions, it may also be possible to
        approximate these features on other top-level entities

    Args:
        features (list[:class:`.PrimitiveBase`]): if these features are dependent
            on aggregation features on the prediction, the approximate values
            for the aggregation feature will be calculated

        cutoff_time (pd.DataFrame): specifies what time to calculate
            the features for each instance at.  A DataFrame with
            'instance_id' and 'time' columns.

        window (Timedelta or str): frequency to group instances with similar
            cutoff times by for features with costly calculations. For example,
            if bucket is 24 hours, all instances with cutoff times on the same
            day will use the same calculation for expensive features.

        entityset (:class:`.EntitySet`): An already initialized entityset.

        training_window (dict[str-> :class:`Timedelta`] or :class:`Timedelta`, optional):
            Window or windows defining how much older than the cutoff time data
            can be to be included when calculating the feature.  To specify
            which entities to apply windows to, use a dictionary mapping entity
            id -> Timedelta. If None, all older data is used.

        verbose (Optional(boolean)): Print progress info.

        profile (Optional(boolean)): Enables profiling if True

        save_progress (Optional(str)): path to save intermediate computational results
    '''
    if verbose:
        logger.info("Approximating features...")

    approx_fms_by_entity = {}
    ignored = None
    target_entity = features[0].entity
    target_index_var = target_entity.index

    to_approximate = gather_approximate_features(features)

    target_time_colname = 'target_time'
    cutoff_time[target_time_colname] = cutoff_time['time']
    target_instance_colname = target_index_var
    cutoff_time[target_instance_colname] = cutoff_time['instance_id']
    approx_cutoffs = bin_cutoff_times(cutoff_time.copy(), window)
    cutoff_df_time_var = 'time'
    cutoff_df_instance_var = 'instance_id'
    # should this order be by dependencies so that calculate_feature_matrix
    # doesn't skip approximating something?
    for approx_entity_id, approx_features in to_approximate.items():
        approx_entity_index_var = entityset[approx_entity_id].index
        # Gather associated instance_ids from the approximate entity
        cutoffs_with_approx_e_ids = approx_cutoffs.copy()
        frames = entityset.get_pandas_data_slice([approx_entity_id, target_entity.id],
                                                 target_entity.id,
                                                 cutoffs_with_approx_e_ids[target_instance_colname])

        if frames is not None:
            rvar = entityset.gen_relationship_var(target_entity.id, approx_entity_id)
            parent_instance_frame = frames[approx_entity_id][target_entity.id]
            cutoffs_with_approx_e_ids[rvar] = \
                cutoffs_with_approx_e_ids.merge(parent_instance_frame[[target_index_var, rvar]],
                                                on=target_index_var, how='left')[rvar].values
            new_approx_entity_index_var = rvar

            # Select only columns we care about
            columns_we_want = [target_instance_colname,
                               new_approx_entity_index_var,
                               cutoff_df_time_var,
                               target_time_colname]

            cutoffs_with_approx_e_ids = cutoffs_with_approx_e_ids[columns_we_want]
            cutoffs_with_approx_e_ids = cutoffs_with_approx_e_ids.drop_duplicates()
            cutoffs_with_approx_e_ids.dropna(subset=[new_approx_entity_index_var],
                                             inplace=True)
        else:
            cutoffs_with_approx_e_ids = pd.DataFrame()

        if cutoffs_with_approx_e_ids.empty:
            approx_fms_by_entity = gen_empty_approx_features_df(approx_features)
            continue

        cutoffs_with_approx_e_ids.sort_values([cutoff_df_time_var,
                                               new_approx_entity_index_var], inplace=True)
        # CFM assumes specific column names for cutoff_time argument
        rename = {new_approx_entity_index_var: cutoff_df_instance_var}
        cutoff_time_to_pass = cutoffs_with_approx_e_ids.rename(columns=rename)
        cutoff_time_to_pass = cutoff_time_to_pass[[cutoff_df_instance_var, cutoff_df_time_var]]

        cutoff_time_to_pass.drop_duplicates(inplace=True)
        approx_fm = calculate_feature_matrix(approx_features,
                                             cutoff_time=cutoff_time_to_pass,
                                             training_window=training_window,
                                             approximate=None,
                                             profile=profile)

        approx_fms_by_entity[approx_entity_id] = approx_fm


    # Include entity because we only want to ignore features that
    # are base_features/dependencies of the top level entity we're
    # approximating.
    # For instance, if target entity is sessions, and we're
    # approximating customers.COUNT(sessions.COUNT(log.value)),
    # we could also just want the feature COUNT(log.value)
    # defined on sessions
    # as a first class feature in the feature matrix.
    # Unless we signify to only ignore it as a dependency of
    # a feature defined on customers, we would ignore computing it
    # and pandas_backend would error
    ignored = {
        entity: f.hash()
        for entity, approx_features in to_approximate.items()
        for f in approx_features
    }
    return approx_fms_by_entity, ignored


def datetime_round(dt, freq, round_up=False):
    """
    Taken from comments on the Pandas source: https://github.com/pandas-dev/pandas/issues/4314

    round down Timestamp series to a specified freq
    """
    if round_up:
        round_f = np.ceil
    else:
        round_f = np.floor
    dt = pd.DatetimeIndex(dt)
    freq = to_offset(freq).delta.value
    return pd.DatetimeIndex(((round_f(dt.asi8 / (float(freq))) * freq).astype(np.int64)))


def gather_approximate_features(features):
    to_approximate = defaultdict(list)
    for feature in features:
        if isinstance(feature, DirectFeature):
            base_feature = feature.base_features[0]
            while not isinstance(base_feature, AggregationPrimitive):
                if isinstance(base_feature, DirectFeature):
                    base_feature = base_feature.base_features[0]
                else:
                    break
            if isinstance(base_feature, AggregationPrimitive):
                approx_entity = base_feature.entity.id
                to_approximate[approx_entity].append(base_feature)
    return to_approximate


def gen_empty_approx_features_df(approx_features):
    approx_entity_id = approx_features[0].entity.id
    df = pd.DataFrame(columns=[f.get_name() for f in approx_features])
    df.index.name = approx_features[0].entity.index
    approx_fms_by_entity = {approx_entity_id: df}
    return approx_fms_by_entity
