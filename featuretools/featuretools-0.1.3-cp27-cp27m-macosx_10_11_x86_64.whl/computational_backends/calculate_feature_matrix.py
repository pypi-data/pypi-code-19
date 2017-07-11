import pandas as pd
from .pandas_backend import PandasBackend
from datetime import datetime
from tqdm import tqdm
import sys
from featuretools.primitives import FeatureBase


def calculate_feature_matrix(features, calc_times=None, instance_ids=None,
                             time_last=None, entities=None, relationships=None,
                             entityset=None, training_window=None,
                             verbose=False, profile=False,):
    """Calculates a matrix for a given set of instance ids and calculation times.


    Args:
        features (list[:class:`.FeatureBase`]): Feature definitions to be calculated.

        calc_times (pd.DataFrame): dataframe with 'instance_id' and 'time' columns

        instance_ids (list(ob)): if calc_times isn't provided, list of instance ids.

        time_last (datetime, pd.Timestamp, optional) : Time at which to calculate
            features. If None, assume current time. Ignored if calc_times is
            not None

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

        verbose (str): Print progress info. The time granularity is only per time group.

        profile (boolean): Enables profiling if True
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

    if calc_times is None:
        if time_last is None:
            time_last = datetime.now()

        if instance_ids is None:
            target_entity = features[0].entity
            id_var = target_entity.id_variable
            instance_ids = target_entity.df[id_var].tolist()

        if not isinstance(time_last, list):
            time_last = [time_last] * len(instance_ids)

        # TODO are these sorted correctly?
        map_args = [(id, time) for id, time in zip(instance_ids, time_last)]
        df_args = pd.DataFrame(map_args, columns=['instance_id', 'time'])
        df_args.sort_values('time', inplace=True)
        indices = df_args.index.values
        to_calc = df_args.values
        calc_times = pd.DataFrame(to_calc, columns=['instance_id', 'time'])
    else:
        indices = calc_times.index.values
        to_calc = calc_times.values
        calc_times = pd.DataFrame(to_calc, columns=['instance_id', 'time'])

    backend = PandasBackend(features[0].entityset, features)

    def calc_results(df):
        time_last = df['time'].values[0]
        ids = df['instance_id'].values
        results = backend.calculate_all_features(ids, time_last,
                                                 training_window=training_window,
                                                 profile=profile)
        results = results[[f.get_name() for f in features]]
        return results

    grouped = calc_times.groupby('time', sort=False)
    if verbose:
        tqdm.pandas(desc="calculate_feature_matrix", file=sys.stdout)
        all_features = grouped.progress_apply(calc_results)
    else:
        all_features = grouped.apply(calc_results)

    # inverse_indices = pd.Series(indices).sort_values().index.values
    all_features.sort_index(level="time", inplace=True)
    all_features.reset_index(level='time', drop=True, inplace=True)
    # feature_matrix = all_features.iloc[inverse_indices]
    feature_matrix = all_features
    return feature_matrix
