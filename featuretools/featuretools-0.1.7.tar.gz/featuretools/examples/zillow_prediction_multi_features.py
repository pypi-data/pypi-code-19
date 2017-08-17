import featuretools as ft
from featuretools import variable_types as vtypes
import pandas as pd
import numpy as np
from featuretools.variable_types import Numeric
from featuretools.primitives import CumMean, CumSum, CumMax, CumMin
import featuretools.primitives as ftprims
from dask import delayed
import copy
from distributed import Client
from itertools import product
import os


to_normalize = ['regionidzip',
                'yearbuilt',
                'fips',
                'censustractandblock',
                'roomcnt',
                'buildingqualitytypeid',
                'regionidneighborhood',
                'buildingclasstypeid',
                'numberofstories',
                'poolcnt']
PROPERTIES = "data/properties_2016.csv"
TRAIN = "data/train_2016_v2.csv"
TEST = "data/sample_submission.csv"
PREDICTION_FILE = 'data/zillow_prediction_data.csv'


# number of rows to read from all csv files, None means all rows
NROWS = None


def create_prediction_file():
    times = [pd.Timestamp('{}/1/201{}'.format(month, year))
             for year in range(6, 8)
             for month in range(10, 13)]
    data_test_parcel_ids = pd.read_csv(TEST, usecols=['ParcelId'])['ParcelId'].values
    p = list(product(data_test_parcel_ids, times))
    data_test_index = pd.MultiIndex.from_tuples(p, names=['parcelid', 'transactiondate'])
    data_test = (pd.Series(np.nan, name='logerror', index=data_test_index)
                 .to_frame())
    data_test.reset_index(level='transactiondate', drop=False, inplace=True)
    data_test.reset_index(drop=False, inplace=True)
    data_test.to_csv("data/zillow_prediction_data.csv")


def load_entityset(use_test_data=False, nrows=NROWS):
    """
    <h2>Step 2: Create dataset, entities, and relationships</h2>

    <p>Within featuretools there is a standard format for representing data that is used to set up predictions and build features. A <b><i>EntitySet</i></b> stores information about entities (database table), variables (columns in databse tables), relationships, data types, and the data itself.

    <p>In this step, a entityset is created and linked to the <b><i>transactions</i></b> and <b><i>properties</i></b> data as entities. The relationship between transactions and properties is explicity stored within the entityset as well. Relationships always follow the "one to many" pattern, where an instance of a &#34;parent&#34; entity can map to multiple instance<i>s</i> of &#34;child&#34; entities. In this example, there are multiple transactions for a unique parcel id in properties. Thus, the parent entity is the properties and the child entities are the individual transactions.</p>
    """
    # fields of properties_2016.csv to read, since many columns contains almost all null values
    usecols = ['parcelid', 'airconditioningtypeid',
               'bathroomcnt', 'buildingclasstypeid',
               'buildingqualitytypeid', 'calculatedbathnbr',
               'calculatedfinishedsquarefeet',
               'fips', 'fullbathcnt',
               'garagetotalsqft', 'hashottuborspa',
               'heatingorsystemtypeid',
               'lotsizesquarefeet', 'poolcnt',
               'regionidneighborhood', 'regionidzip',
               'roomcnt', 'yearbuilt',
               'numberofstories', 'structuretaxvaluedollarcnt',
               'taxvaluedollarcnt', 'assessmentyear',
               'taxamount', 'censustractandblock']

    data_properties = pd.read_csv(PROPERTIES,
                                  dtype={'airconditioningtypeid': "object",
                                         'buildingclasstypeid': "object",
                                         'buildingqualitytypeid': "object",
                                         'heatingorsystemtypeid': "object",
                                         'propertylandusetypeid': "object",
                                         'hashottuborspa': "bool"},
                                  parse_dates=['assessmentyear', 'yearbuilt'],
                                  low_memory=False,
                                  usecols=usecols)
    data_transactions = pd.read_csv(TRAIN,
                                    parse_dates=['transactiondate'])
    if nrows is not None:
        parcel_ids = data_transactions['parcelid'].drop_duplicates()
        if len(parcel_ids) > nrows:
            parcel_ids = parcel_ids.sample(nrows)
        data_transactions = data_transactions[data_transactions['parcelid'].isin(parcel_ids)]
        data_properties = data_properties.merge(parcel_ids.to_frame(),
                                                left_on='parcelid',
                                                right_on='parcelid',
                                                how='inner')

    if use_test_data:
        if not os.path.exists(PREDICTION_FILE):
            create_prediction_file()
        data_test = pd.read_csv(PREDICTION_FILE,
                                parse_dates=['transactiondate'])
        if nrows is not None:
            data_test = data_test.sample(nrows)
        data_transactions = pd.concat([data_transactions, data_test])

    # Create EntitySet
    es = ft.EntitySet("zillow")

    # Add entity "transactions" to dataset
    es.entity_from_dataframe("transactions",
                             dataframe=data_transactions,
                             index="transaction_id",
                             make_index=True,
                             time_index='transactiondate')
    property_variable_types = {
        'regionidzip': vtypes.Categorical,
        'yearbuilt': vtypes.Ordinal,
        'fips': vtypes.Discrete,
        'censustractandblock': vtypes.Categorical,
        'roomcnt': vtypes.Ordinal,
        'buildingqualitytypeid': vtypes.Categorical,
        'regionidneighborhood': vtypes.Categorical,
        'buildingclasstypeid': vtypes.Categorical,
        'numberofstories': vtypes.Ordinal,
        'poolcnt': vtypes.Ordinal
    }
    # Add entity "properties" to dataset
    es.entity_from_dataframe("properties",
                             dataframe=data_properties,
                             index="parcelid",
                             variable_types=property_variable_types)

    # Build Relationships
    es.add_relationships([ft.Relationship(es['properties']['parcelid'], es['transactions']['parcelid'])])

    # Normalize some categorical variables to generate better features

    for var in to_normalize:
        # Make sure to convert links to integers because
        # we have many missing values. So NaN's will map
        # to a particular number in the link variable
        es.normalize_entity('properties', var, index=var,
                            convert_links_to_integers=True)

    # this allows us to create features that are conditioned on a second value before we calculate.
    es.add_interesting_values(verbose=True)
    return es


def define_features(es, max_features=None):
    cum_prims = [CumMean,
                 CumMax,
                 CumMin,
                 CumSum]

    use_previous_options = ["1 year", "2 years"]

    to_group_cum = [ft.Feature(es['properties'][v], es['transactions'])
                    for v in to_normalize]
    cum_feats = [Prim(v, groupby, use_previous=up)
                 for v in es['transactions'].variables
                 for groupby in to_group_cum
                 for Prim in cum_prims
                 for up in use_previous_options
                 if isinstance(v, Numeric)]

    trans_primitives = [ftprims.Year, ftprims.TimeSince]

    agg_primitives = [ftprims.Sum, ftprims.Std, ftprims.Max, ftprims.Skew,
                      ftprims.Min, ftprims.Mean, ftprims.Count,
                      ftprims.PercentTrue, ftprims.NUnique, ftprims.Mode,
                      ftprims.Trend]  # , ftprims.TopNMostCommon]

    drop_contains = []
    for ne in to_normalize:
        drop_contains.append('{}.SKEW(properties.'.format(ne))
        drop_contains.append('{}.STD(properties.'.format(ne))
        drop_contains.append('{}.{}'.format(ne, ne))

        for ap in agg_primitives:
            drop_contains.append('{}.{}(transactions.CUM'.format(ne, ap.name.upper()))
            for ap2 in agg_primitives:
                drop_contains.append('properties.{}.{}(properties.{}(transactions.'.format(ne, ap2.name.upper(), ap2.name.upper()))

    for ap in agg_primitives:
        drop_contains.append('properties.{}(transactions.CUM'.format(ap.name.upper()))

    features = ft.dfs(entityset=es,
                      target_entity="transactions",
                      seed_features=cum_feats,
                      max_depth=3,
                      features_only=True,
                      agg_primitives=agg_primitives,
                      trans_primitives=trans_primitives,
                      drop_contains=drop_contains,
                      verbose=True)
    if max_features:
        features = list(np.random.choice(features, max_features))
    return features


def get_feature_matrix(features, num_instances=None, instance_ids=None,
                       delayed_calc=True, n_partitions=64,
                       host='54.87.193.12:8786',
                       parallelize_by='features'):
    es = features[0].entityset
    if num_instances is None and instance_ids is None:
        instance_ids = es.get_all_instances("transactions")
    elif instance_ids is None:
        instance_ids = np.sort(es.sample_instances("transactions", num_instances))
    cutoff_time = (es['transactions'].df[['transaction_id', 'transactiondate']]
                                     .rename(columns={'transaction_id': 'instance_id',
                                                      'transactiondate': 'time'}))

    ids_frame = pd.Series(instance_ids, name='instance_id').to_frame()
    cutoff_time = cutoff_time.merge(ids_frame, left_on='instance_id', right_on='instance_id', how='inner')
    cfm_kwargs = dict(
        features=features,
        cutoff_time=cutoff_time,
        instance_ids=instance_ids,
        approximate="1 year",
        verbose=True)
    if not delayed_calc:
        return ft.calculate_feature_matrix(**cfm_kwargs)

    if parallelize_by == 'features':
        iterable = features
    else:
        iterable = [g for n, g in cutoff_time.groupby('time', sort=True)]
    partition_size = len(iterable) / n_partitions
    leftover = len(iterable) - (n_partitions * partition_size)
    partition_sizes = [partition_size for p in range(n_partitions)]
    for i in range(leftover):
        partition_sizes[i] += 1

    start = 0
    outputs = []
    for p, size in zip(range(n_partitions), partition_sizes):
        end = start + size
        partition = iterable[start: end]
        cfm_kwargs = copy.copy(cfm_kwargs)
        if parallelize_by == 'features':
            cfm_kwargs['features'] = partition
        else:
            partition = pd.concat(partition)
            cfm_kwargs['cutoff_time'] = partition

        start += size
        outputs.append(delayed(ft.calculate_feature_matrix)(**cfm_kwargs))
    assert end == len(iterable)

    if parallelize_by == 'features':
        feature_matrix_delayed = delayed(pd.concat)(outputs, axis=1)
    else:
        feature_matrix_delayed = delayed(pd.concat)(outputs)
    c = Client(host)
    feature_matrix = c.compute(feature_matrix_delayed, sync=False)
    return feature_matrix


if __name__ == '__main__':
    import cPickle as pck
    # feature_file = 'high_variance_features.p'
    # with open(feature_file, 'rb') as f:
        # features = pck.load(f)
    # load full es
    es = load_entityset(use_test_data=False)
    print "LOADED ES"
    features = define_features(es)
    # print "DEFINED FEATS"
    # feature_matrix = get_feature_matrix(features, num_instances=100, delayed_calc=False)
    # feature_matrix.to_pickle('many_features_fm.p')
    # print "GOT FM ANS AVED TO PCK"
    # from featuretools.selection.variance_selection import select_high_variance_features
    # hv_fm, hv_f = select_high_variance_features(feature_matrix, features, threshold=20, categorical_nunique_ratio=.1)
    # print "SELECTED HV"
    feature_file = 'high_variance_features.p'
    # with open(feature_file, 'wb') as f:
        # pck.dump(hv_f, f)
    # hv_fm.to_pickle("hv_feature_matrix_100.p")
    print "DUMPED"
    with open(feature_file, 'rb') as f:
        hv_f = pck.load(f)
    hv_feat_names = set([f.get_name() for f in hv_f])
    hv_f = [f for f in features if f.get_name() in hv_feat_names]
    #host = '54.87.193.12:8786'
    fm = get_feature_matrix(hv_f, delayed_calc=False)
    print "GOT FULL FM"
    #fm_delayed = get_feature_matrix(features, num_instances=100, n_partitions=32, parallelize_by='time')
    #fm = fm_delayed.result()
    fm.to_pickle("high_variance_fm_full.p")
    print "DUMPED"

    to_encode = [f for f in hv_f if f.get_name() not in ('parcelid', 'logerror')]
    fm.drop(['parcelid', 'logerror'], axis=1, inplace=True)
    encoded_fm, encoded_features = ft.encode_features(fm, to_encode)
    print "ENCODED"
    encoded_fm.to_pickle("high_variance_fm_full_encoded.p")
    feature_file = 'high_variance_features_encoded.p'
    with open(feature_file, 'wb') as f:
        pck.dump(encoded_features, f)
    print "DUMPED"
