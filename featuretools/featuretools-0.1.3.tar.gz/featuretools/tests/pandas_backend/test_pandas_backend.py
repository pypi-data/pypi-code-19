import pytest
from featuretools.computational_backends.pandas_backend import PandasBackend
from featuretools.primitives import (IdentityFeature, DirectFeature, Sum,
                                     Count, Min, Mode, Compare, Mean, And,
                                     TopNMostCommon)
from featuretools import Timedelta
from featuretools import calculate_feature_matrix
from ..testing_utils import make_ecommerce_entityset
from datetime import datetime


@pytest.fixture(scope='module')
def entityset():
    return make_ecommerce_entityset()


@pytest.fixture
def backend(entityset):
    def inner(features):
        return PandasBackend(entityset, features)
    return inner


def test_make_identity(entityset, backend):
    f = IdentityFeature(entityset['log']['datetime'])

    pandas_backend = backend([f])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[f.get_name()][0]
    assert (v == datetime(2011, 4, 9, 10, 30, 0))


def test_make_dfeat(entityset, backend):
    f = DirectFeature(base_feature=entityset['customers']['age'],
                      child_entity=entityset['sessions'])

    pandas_backend = backend([f])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[f.get_name()][0]
    assert (v == 33)


def test_make_agg_feat_of_identity_variable(entityset, backend):
    agg_feat = Sum(base_feature=entityset['log']['value'],
                   parent_entity=entityset['sessions'])

    pandas_backend = backend([agg_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[agg_feat.get_name()][0]
    assert (v == 50)


def test_make_agg_feat_of_identity_id_variable(entityset, backend):
    agg_feat = Count(base_feature=entityset['log']['id'],
                     parent_entity=entityset['sessions'])

    pandas_backend = backend([agg_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[agg_feat.get_name()][0]
    assert (v == 5)


def test_make_agg_feat_where_count(entityset, backend):
    agg_feat = Count(base_feature=entityset['log']['id'],
                     parent_entity=entityset['sessions'],
                     where=IdentityFeature(entityset['log']['product_id']) == 'coke zero')

    pandas_backend = backend([agg_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)

    v = df[agg_feat.get_name()][0]
    assert (v == 3)


def test_make_agg_feat_using_prev_time(entityset, backend):
    agg_feat = Count(base_feature=entityset['log']['id'],
                     parent_entity=entityset['sessions'],
                     use_previous=Timedelta(10, 's'))

    pandas_backend = backend([agg_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=datetime(2011, 4, 9, 10, 30, 10))

    v = df[agg_feat.get_name()][0]
    assert (v == 2)

    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=datetime(2011, 4, 9, 10, 30, 30))

    v = df[agg_feat.get_name()][0]
    assert (v == 1)


def test_make_agg_feat_using_prev_n_events(entityset, backend):
    agg_feat_1 = Min(base_feature=entityset['log']['value'],
                     parent_entity=entityset['sessions'],
                     use_previous=Timedelta(1, 'observations',
                                            entity=entityset['log']))

    agg_feat_2 = Min(base_feature=entityset['log']['value'],
                     parent_entity=entityset['sessions'],
                     use_previous=Timedelta(3, 'observations',
                                            entity=entityset['log']))

    assert agg_feat_1.get_name() != agg_feat_2.get_name(), \
        'Features should have different names based on use_previous'

    pandas_backend = backend([agg_feat_1, agg_feat_2])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=datetime(2011, 4, 9, 10, 30, 6))

    # time_last is included by default
    v1 = df[agg_feat_1.get_name()][0]
    v2 = df[agg_feat_2.get_name()][0]
    assert v1 == 5
    assert v2 == 0

    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=datetime(2011, 4, 9, 10, 30, 30))

    v1 = df[agg_feat_1.get_name()][0]
    v2 = df[agg_feat_2.get_name()][0]
    assert v1 == 20
    assert v2 == 10


def test_make_agg_feat_multiple_dtypes(entityset, backend):
    compare_prod = IdentityFeature(entityset['log']['product_id']) == 'coke zero'

    agg_feat = Count(base_feature=entityset['log']['id'],
                     parent_entity=entityset['sessions'],
                     where=compare_prod)

    agg_feat2 = Mode(base_feature=entityset['log']['product_id'],
                     parent_entity=entityset['sessions'],
                     where=compare_prod)

    pandas_backend = backend([agg_feat, agg_feat2])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)

    v = df[agg_feat.get_name()][0]
    v2 = df[agg_feat2.get_name()][0]
    assert (v == 3)
    assert (v2 == 'coke zero')


def test_make_agg_feat_where_different_identity_feat(entityset, backend):
    feats = []
    where_cmps = [Compare.LT, Compare.GT, Compare.LE, Compare.GE, Compare.EQ, Compare.NE]
    for where_cmp in where_cmps:
        feats.append(Count(base_feature=entityset['log']['id'],
                           parent_entity=entityset['sessions'],
                           where=Compare(entityset['log']['datetime'],
                                         where_cmp,
                                         datetime(2011, 4, 10, 10, 40, 1))))

    pandas_backend = backend(feats)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2, 3],
                                               time_last=None)

    for i, where_cmp in enumerate(where_cmps):
        feat = feats[i]
        name = feat.get_name()
        instances = df[name]
        v0, v1, v2, v3 = instances[0:4]
        if where_cmp == '<':
            assert (v0 == 5)
            assert (v1 == 4)
            assert (v2 == 1)
            assert (v3 == 1)
        elif where_cmp == '>':
            assert (v0 == 0)
            assert (v1 == 0)
            assert (v2 == 0)
            assert (v3 == 0)
        elif where_cmp == '<=':
            assert (v0 == 5)
            assert (v1 == 4)
            assert (v2 == 1)
            assert (v3 == 2)
        elif where_cmp == '>=':
            assert (v0 == 0)
            assert (v1 == 0)
            assert (v2 == 0)
            assert (v3 == 1)
        elif where_cmp == '=':
            assert (v0 == 0)
            assert (v1 == 0)
            assert (v2 == 0)
            assert (v3 == 1)
        elif where_cmp == '!=':
            assert (v0 == 5)
            assert (v1 == 4)
            assert (v2 == 1)
            assert (v3 == 1)


def test_make_agg_feat_of_grandchild_entity(entityset, backend):
    agg_feat = Count(base_feature=entityset['log']['id'],
                     parent_entity=entityset['customers'])

    pandas_backend = backend([agg_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[agg_feat.get_name()][0]
    assert (v == 10)


def test_make_agg_feat_where_count_feat(entityset, backend):
    """
    Feature we're creating is:
    Number of sessions for each customer where the
    number of logs in the session is less than 3
    """
    Count.max_stack_depth = 2
    log_count_feat = Count(base_feature=entityset['log']['id'],
                           parent_entity=entityset['sessions'])

    feat = Count(base_feature=entityset['sessions']['id'],
                 parent_entity=entityset['customers'],
                 where=log_count_feat > 1)

    assert (feat.can_apply(entityset['customers'], 'customers'))
    pandas_backend = backend([feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1],
                                               time_last=None)
    name = feat.get_name()
    instances = df[name]
    v0, v1 = instances[0:2]
    assert (v0 == 2)
    assert (v1 == 2)


def test_make_compare_feat(entityset, backend):
    """
    Feature we're creating is:
    Number of sessions for each customer where the
    number of logs in the session is less than 3
    """
    Count.max_stack_depth = 2
    log_count_feat = Count(base_feature=entityset['log']['id'],
                           parent_entity=entityset['sessions'])

    mean_agg_feat = Mean(log_count_feat,
                         parent_entity=entityset['customers'])

    mean_feat = DirectFeature(base_feature=mean_agg_feat,
                              child_entity=entityset['sessions'])

    feat = log_count_feat > mean_feat

    pandas_backend = backend([feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2],
                                               time_last=None)
    name = feat.get_name()
    instances = df[name]
    v0, v1, v2 = instances[0:3]
    assert v0
    assert v1
    assert not v2


def test_make_agg_feat_where_count_and_device_type_feat(entityset, backend):
    """
    Feature we're creating is:
    Number of sessions for each customer where the
    number of logs in the session is less than 3
    """
    Count.max_stack_depth = 2
    log_count_feat = Count(base_feature=entityset['log']['id'],
                           parent_entity=entityset['sessions'])

    compare_count = log_count_feat == 1
    compare_device_type = IdentityFeature(entityset['sessions']['device_type']) == 1
    and_feat = And(compare_count, compare_device_type)
    feat = Count(base_feature=entityset['sessions']['id'],
                 parent_entity=entityset['customers'],
                 where=and_feat)

    assert (feat.can_apply(entityset['customers'], 'customers'))
    pandas_backend = backend([feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    name = feat.get_name()
    instances = df[name]
    assert (instances[0] == 1)


def test_make_agg_feat_where_count_or_device_type_feat(entityset, backend):
    """
    Feature we're creating is:
    Number of sessions for each customer where the
    number of logs in the session is less than 3
    """
    Count.max_stack_depth = 2
    log_count_feat = Count(entityset['log']['id'],
                           parent_entity=entityset['sessions'])

    compare_count = log_count_feat > 1
    compare_device_type = IdentityFeature(entityset['sessions']['device_type']) == 1
    or_feat = compare_count.OR(compare_device_type)
    feat = Count(base_feature=entityset['sessions']['id'],
                 parent_entity=entityset['customers'],
                 where=or_feat)

    assert (feat.can_apply(entityset['customers'], 'customers'))
    pandas_backend = backend([feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    name = feat.get_name()
    instances = df[name]
    assert (instances[0] == 3)


def test_make_agg_feat_of_agg_feat(entityset, backend):
    log_count_feat = Count(entityset['log']['id'],
                           parent_entity=entityset['sessions'])

    customer_sum_feat = Sum(base_feature=log_count_feat,
                            parent_entity=entityset['customers'])

    pandas_backend = backend([customer_sum_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[customer_sum_feat.get_name()][0]
    assert (v == 10)


def test_make_dfeat_of_agg_feat_on_self(entityset, backend):
    """
    The graph looks like this:

        R       R = Regions, a parent of customers
        |
        C       C = Customers, the entity we're trying to predict on
        |
       etc.

    We're trying to calculate a DFeat from C to R on an agg_feat of R on C.
    """
    customer_count_feat = Count(base_feature=entityset['customers']['id'],
                                parent_entity=entityset['regions'])

    num_customers_feat = DirectFeature(base_feature=customer_count_feat,
                                       child_entity=entityset['customers'])

    pandas_backend = backend([num_customers_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[num_customers_feat.get_name()][0]
    assert (v == 3)


def test_make_dfeat_of_agg_feat_through_parent(entityset, backend):
    """
    The graph looks like this:

        R       C = Customers, the entity we're trying to predict on
       / \      R = Regions, a parent of customers
      S   C     S = Stores, a child of regions
          |
         etc.

    We're trying to calculate a DFeat from C to R on an agg_feat of R on S.
    """
    store_id_feat = IdentityFeature(entityset['stores']['id'])

    store_count_feat = Count(base_feature=store_id_feat,
                             parent_entity=entityset['regions'])

    num_stores_feat = DirectFeature(base_feature=store_count_feat,
                                    child_entity=entityset['customers'])

    pandas_backend = backend([num_stores_feat])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[num_stores_feat.get_name()][0]
    assert (v == 3)


def test_make_deep_agg_feat_of_dfeat_of_agg_feat(entityset, backend):
    """
    The graph looks like this (higher implies parent):

          C     C = Customers, the entity we're trying to predict on
          |     S = Sessions, a child of Customers
      P   S     L = Log, a child of both Sessions and Log
       \ /      P = Products, a parent of Log which is not a descendent of customers
        L

    We're trying to calculate a DFeat from L to P on an agg_feat of P on L, and
    then aggregate it with another agg_feat of C on L.
    """
    log_count_feat = Count(entityset['log']['id'],
                           parent_entity=entityset['products'])

    product_purchases_feat = DirectFeature(base_feature=log_count_feat,
                                           child_entity=entityset['log'])

    purchase_popularity = Mean(base_feature=product_purchases_feat,
                               parent_entity=entityset['customers'])

    pandas_backend = backend([purchase_popularity])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[purchase_popularity.get_name()][0]
    assert (v == 38.0 / 10.0)


def test_deep_agg_feat_chain(entityset, backend):
    """
    Agg feat of agg feat:
        region.Mean(customer.Count(Log))
    """
    customer_count_feat = Count(entityset['log']['id'],
                                parent_entity=entityset['customers'])

    region_avg_feat = Mean(base_feature=customer_count_feat,
                           parent_entity=entityset['regions'])

    pandas_backend = backend([region_avg_feat])
    df = pandas_backend.calculate_all_features(instance_ids=['United States'],
                                               time_last=None)
    v = df[region_avg_feat.get_name()][0]
    assert (v == 17 / 3.)


def test_topn(entityset, backend):
    topn = TopNMostCommon(entityset['log']['product_id'],
                          entityset['customers'], n=3)
    pandas_backend = backend([topn])

    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2],
                                               time_last=None)

    true_results = [
        ['toothpaste', 'coke zero', 'brown bag'],
        ['coke zero', 'Haribo sugar-free gummy bears'],
        ['taco clock']
    ]
    assert (topn.get_name() in df.columns)
    for i, values in enumerate(df[topn.get_name()].values):
        for j, v in enumerate(values):
            assert (v == true_results[i][j])


# TODO test mean ignores nan values
def test_calc_feature_matrix(entityset):
    times = list([datetime(2011, 4, 9, 10, 30, i * 6) for i in range(5)] +
                 [datetime(2011, 4, 9, 10, 31, i * 9) for i in range(4)] +
                 [datetime(2011, 4, 9, 10, 40, 0)] +
                 [datetime(2011, 4, 10, 10, 40, i) for i in range(2)] +
                 [datetime(2011, 4, 10, 10, 41, i * 3) for i in range(3)] +
                 [datetime(2011, 4, 10, 11, 10, i * 3) for i in range(2)])
    labels = [False] * 3 + [True] * 2 + [False] * 9 + [True] + [False] * 2

    property_feature = IdentityFeature(entityset['log']['value']) > 10

    feature_matrix = calculate_feature_matrix([property_feature], instance_ids=range(17),
                                              time_last=times)

    assert (feature_matrix == labels).values.all()

    with pytest.raises(AssertionError):
        feature_matrix = calculate_feature_matrix('features', instance_ids=range(17),
                                                  time_last=times)
    with pytest.raises(AssertionError):
        feature_matrix = calculate_feature_matrix([], instance_ids=range(17),
                                                  time_last=times)
    with pytest.raises(AssertionError):
        feature_matrix = calculate_feature_matrix([1, 2, 3], instance_ids=range(17),
                                                  time_last=times)


def test_handles_time_last_correctly(entityset):
    property_feature = Count(entityset['log']['id'], entityset['customers'])
    feature_matrix = calculate_feature_matrix([property_feature], instance_ids=[0, 1, 2],
                                              time_last=[datetime(2011, 4, 10), datetime(2011, 4, 11),
                                              datetime(2011, 4, 7)])
    labels = [0, 10, 5]
    assert (feature_matrix == labels).values.all()


def test_handles_training_window_correctly(entityset):
    property_feature = Count(entityset['log']['id'], entityset['customers'])
    feature_matrix = calculate_feature_matrix([property_feature],
                                              instance_ids=[0, 1, 2],
                                              time_last=[datetime(2011, 4, 9, 12, 31),
                                                         datetime(2011, 4, 10, 11),
                                                         datetime(2011, 4, 10, 13, 10, 1)],
                                              training_window={'log': '2 hours'})
    labels = [5, 5, 1]
    assert (feature_matrix == labels).values.all()

    property_feature = Count(entityset['log']['id'], entityset['customers'])
    feature_matrix = calculate_feature_matrix([property_feature],
                                              instance_ids=[0, 1, 2],
                                              time_last=[datetime(2011, 4, 9, 12, 31),
                                                         datetime(2011, 4, 10, 11),
                                                         datetime(2011, 4, 10, 13, 10, 1)],
                                              training_window='2 hours')
    labels = [0, 0, 0]
    assert (feature_matrix == labels).values.all()

    with pytest.raises(AssertionError):
        feature_matrix = calculate_feature_matrix([property_feature],
                                                  instance_ids=[0, 1, 2],
                                                  time_last=[datetime(2011, 4, 9, 12, 31),
                                                             datetime(2011, 4, 10, 11),
                                                             datetime(2011, 4, 10, 13, 10, 1)],
                                                  training_window=Timedelta(2, 'observations', entity='log'))
