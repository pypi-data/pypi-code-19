import pandas as pd
from .pandas_backend import PandasBackend
from datetime import datetime, timedelta
from tqdm import tqdm
from featuretools.primitives import FeatureBase, AggregationFeature, DirectFeature
from collections import defaultdict
from featuretools.utils.wrangle import _check_timedelta
import os
import sys
from functools import wraps
import shutil


def calculate_feature_matrix(features, cutoff_time=None, instance_ids=None,
                             entities=None, relationships=None, entityset=None,
                             training_window=None, approximate=None,
                             save_progress=None, verbose=False,
                             verbose_desc='calculate_feature_matrix',
                             profile=False):
    """Calculates a matrix for a given set of instance ids and calculation times.

    Args:
        features (list[:class:`.FeatureBase`]): Feature definitions to be calculated.

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

        approximate (Timedelta): bucket size to group instances with similar
            cutoff times by for features with costly calculations. For example,
            if bucket is 24 hours, all instances with cutoff times on the same
            day will use the same calculation for expensive features.

        verbose (Optional(boolean)): Print progress info. The time granularity is only per time group.

        profile (Optional(boolean)): Enables profiling if True

        save_progress (Optional(str)): path where to save intermediate computational results
    """
    assert (isinstance(features, list) and features != [] and
            all([isinstance(feature, FeatureBase) for feature in features])), \
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
            id_var = target_entity.id_variable
            instance_ids = target_entity.df[id_var].tolist()

        if not isinstance(cutoff_time, list):
            cutoff_time = [cutoff_time] * len(instance_ids)

        # TODO are these sorted correctly?
        map_args = [(id, time) for id, time in zip(instance_ids, cutoff_time)]
        df_args = pd.DataFrame(map_args, columns=['instance_id', 'time'])
        df_args.sort_values('time', inplace=True)
        to_calc = df_args.values
        cutoff_time = pd.DataFrame(to_calc, columns=['instance_id', 'time'])
    else:
        to_calc = cutoff_time.values
        cutoff_time = pd.DataFrame(to_calc, columns=['instance_id', 'time'])

    if approximate is not None:
        precalculated_features, ignored = approximate_features(features,
                                                               cutoff_time,
                                                               approximate,
                                                               entityset,
                                                               training_window=training_window,
                                                               verbose=verbose,
                                                               profile=profile)
    else:
        precalculated_features = None
        ignored = None

    backend = PandasBackend(entityset,
                            features,
                            precalculated_features=precalculated_features,
                            ignored=ignored)

    few_cutoff_times = cutoff_time['time'].nunique() == 1
    backend_verbose = verbose and few_cutoff_times

    @save_csv_decorator(save_progress)
    def calc_results(time_last, ids):
        results = backend.calculate_all_features(ids, time_last,
                                                 training_window=training_window,
                                                 profile=profile,
                                                 verbose=backend_verbose)
        results = results[[f.get_name() for f in features]]
        return results

    grouped = cutoff_time.groupby('time', sort=False)

    if verbose:
        iterator = tqdm(grouped,
                        desc=verbose_desc,
                        total=len(grouped),
                        file=sys.stdout)
    else:
        iterator = grouped

    all_features = None
    for _, group in iterator:
        time_last = group['time'].iloc[0]
        ids = group['instance_id'].values
        results = calc_results(time_last, ids)
        results.index = pd.MultiIndex.from_product([[time_last], ids], names=['time', 'instance_id'])
        if all_features is None:
            all_features = results
        else:
            all_features = pd.concat([all_features, results])

    if save_progress and os.path.exists(os.path.join(save_progress, 'temp')):
        shutil.rmtree(os.path.join(save_progress, 'temp'))
    all_features.sort_index(level="time", inplace=True)
    all_features.reset_index(level='time', drop=True, inplace=True)
    feature_matrix = all_features
    return feature_matrix


# TODO: convert days to microseconds, add tuple option to change reference point
def bin_cutoff_times(cuttoff_time, bin_size):
    DAY_IN_MICROSECONDS = 86400000000
    HOUR_IN_MICROSECONDS = 3600000000
    MINUTE_IN_MICROSECONDS = 60000000
    SECOND_IN_MICROSECONDS = 1000000
    binned_cutoff_time = cuttoff_time.copy()
    if type(bin_size) == int:
        binned_cutoff_time['time'] = binned_cutoff_time['time'].apply(lambda x: x / bin_size * bin_size)
    else:
        bin_size = _check_timedelta(bin_size).get_pandas_timedelta()
        bin_microseconds = (bin_size.days * DAY_IN_MICROSECONDS +
                            bin_size.seconds * 1000000 + bin_size.microseconds)

        def bin_df(x):
            x_us = (((x.toordinal() * 24 + x.hour) * 60 + x.minute) * 60 + x.second) * 1000000 + x.microsecond
            binned_us = x_us % bin_microseconds
            days = binned_us / DAY_IN_MICROSECONDS
            hours = binned_us % DAY_IN_MICROSECONDS / HOUR_IN_MICROSECONDS
            minutes = binned_us % DAY_IN_MICROSECONDS % HOUR_IN_MICROSECONDS / MINUTE_IN_MICROSECONDS
            seconds = binned_us % DAY_IN_MICROSECONDS % HOUR_IN_MICROSECONDS % MINUTE_IN_MICROSECONDS / SECOND_IN_MICROSECONDS
            microseconds = binned_us % DAY_IN_MICROSECONDS % HOUR_IN_MICROSECONDS % MINUTE_IN_MICROSECONDS % SECOND_IN_MICROSECONDS
            return x - timedelta(days=days,
                                 hours=hours,
                                 minutes=minutes,
                                 seconds=seconds,
                                 microseconds=microseconds)
        binned_cutoff_time['time'] = binned_cutoff_time['time'].apply(bin_df)
    return binned_cutoff_time


def bin_cutoff_time(cutoff_time, bin_size):
    if type(bin_size) == int:
        binned_time = cutoff_time / bin_size * bin_size
    else:
        DAY_IN_MICROSECONDS = 86400000000
        HOUR_IN_MICROSECONDS = 3600000000
        MINUTE_IN_MICROSECONDS = 60000000
        SECOND_IN_MICROSECONDS = 1000000
        bin_size = _check_timedelta(bin_size).get_pandas_timedelta()
        bin_microseconds = (bin_size.days * DAY_IN_MICROSECONDS +
                            bin_size.seconds * SECOND_IN_MICROSECONDS +
                            bin_size.microseconds)

        converted_time = (((cutoff_time.toordinal() * 24 + cutoff_time.hour) * 60 + cutoff_time.minute) * 60 + cutoff_time.second) * 1000000 + cutoff_time.microsecond
        binned_us = converted_time % bin_microseconds
        days = binned_us / DAY_IN_MICROSECONDS
        hours = binned_us % DAY_IN_MICROSECONDS / HOUR_IN_MICROSECONDS
        minutes = binned_us % DAY_IN_MICROSECONDS % HOUR_IN_MICROSECONDS / MINUTE_IN_MICROSECONDS
        seconds = binned_us % DAY_IN_MICROSECONDS % HOUR_IN_MICROSECONDS % MINUTE_IN_MICROSECONDS / SECOND_IN_MICROSECONDS
        microseconds = binned_us % DAY_IN_MICROSECONDS % HOUR_IN_MICROSECONDS % MINUTE_IN_MICROSECONDS % SECOND_IN_MICROSECONDS
        binned_time = cutoff_time - timedelta(days=days,
                                              hours=hours,
                                              minutes=minutes,
                                              seconds=seconds,
                                              microseconds=microseconds)
    return binned_time


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

    Args:
        features (list[:class:`.FeatureBase`]): if these features are dependent
            on aggregation features on the prediction, the approximate values
            for the aggregation feature will be calculated

        cutoff_time (pd.DataFrame): specifies what time to calculate
            the features for each instance at.  A DataFrame with
            'instance_id' and 'time' columns.

        window (Timedelta): bucket size to group instances with similar
            cutoff times by for features with costly calculations. For example,
            if bucket is 24 hours, all instances with cutoff times on the same
            day will use the same calculation for expensive features.

        entityset (:class:`.EntitySet`): An already initialized entityset.

        training_window (dict[str-> :class:`Timedelta`] or :class:`Timedelta`, optional):
            Window or windows defining how much older than the cutoff time data
            can be to be included when calculating the feature.  To specify
            which entities to apply windows to, use a dictionary mapping entity
            id -> Timedelta. If None, all older data is used.

        verbose (Optional(boolean)): Print progress info. The time granularity is only per time group.

        profile (Optional(boolean)): Enables profiling if True

        save_progress (Optional(str)): path where to save intermediate computational results
    '''
    to_approximate = defaultdict(list)
    precalculated_features = defaultdict(dict)
    ignored = None
    target_entity = features[0].entity
    for feature in features:
        if isinstance(feature, DirectFeature):
            deps = feature._get_deep_dependencies()
            for dep in deps:
                if isinstance(dep, AggregationFeature):
                    approx_entity = dep.entity_id
                    to_approximate[approx_entity].append(dep)

    # should this order be by dependencies so that calculate_feature_matrix
    # doesn't skip approximating something
    for entity_id in to_approximate:
        approx_cutoffs = cutoff_time.copy()

        # Bin cutoff times
        approx_cutoffs['child_time'] = approx_cutoffs['time']
        approx_cutoffs = bin_cutoff_times(approx_cutoffs, window)

        # Figure out which instance_ids to take
        approx_cutoffs['child_instance'] = approx_cutoffs['instance_id']
        # TODO: only forward path or support backward path?
        path = entityset.find_forward_path(target_entity.id, entity_id)

        def get_forward_instance_id(x, relationship):
            instance_id = relationship.child_entity.df[relationship.child_variable.id][x]
            return instance_id

        for relationship in path:
            # TODO change apply
            approx_cutoffs['instance_id'] = approx_cutoffs['instance_id'].apply(get_forward_instance_id,
                                                                                args=(relationship,))
        binned_cutoffs = approx_cutoffs[['instance_id', 'time']].drop_duplicates()
        binned_cutoffs.sort_values(['time', 'instance_id'], inplace=True)
        approx_features = calculate_feature_matrix(to_approximate[entity_id],
                                                   cutoff_time=binned_cutoffs,
                                                   training_window=training_window,
                                                   verbose=verbose,
                                                   verbose_desc="approximate_features",
                                                   profile=profile)
        binned_cutoffs.index = binned_cutoffs['instance_id']
        approx_features = pd.concat([binned_cutoffs, approx_features], axis=1)
        approx_features = pd.merge(approx_cutoffs,
                                   approx_features,
                                   on=['instance_id', 'time'])
        approx_features.set_index('instance_id', inplace=True)
        approx_features.drop(['child_instance', 'time'], axis=1, inplace=True)
        approx_features.drop_duplicates(inplace=True)
        grouped = approx_features.groupby('child_time', sort=False)
        for name, group in grouped:
            precalculated_features[name][entity_id] = group.drop('child_time',
                                                                 axis=1)

        ignored = [
            f.hash() for entity_features in to_approximate
            for f in to_approximate[entity_features]
        ]
    return precalculated_features, ignored
