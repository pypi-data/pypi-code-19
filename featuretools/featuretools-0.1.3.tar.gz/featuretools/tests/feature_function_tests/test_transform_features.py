import pytest
from featuretools.computational_backends import PandasBackend
from featuretools.primitives import (Day, Hour, Diff, Compare, Not,
                                   DirectFeature, Count, Add,
                                   Subtract, Multiply, IdentityFeature,
                                   Divide, CumSum, CumCount, CumMin, CumMax,
                                   CumMean, Mod, And, Or, Negate, Sum,
                                   Word2VecCluster, IsIn, Feature, Like)
from featuretools import Timedelta
from ..testing_utils import make_ecommerce_entityset
import numpy as np
from datetime import datetime


@pytest.fixture(scope='module')
def es():
    return make_ecommerce_entityset()


@pytest.fixture(scope='module')
def int_es():
    return make_ecommerce_entityset(with_integer_time_index=True)


def test_make_trans_feat(es):
    f = Hour(es['log']['datetime'])

    pandas_backend = PandasBackend(es, [f])
    df = pandas_backend.calculate_all_features(instance_ids=[0],
                                               time_last=None)
    v = df[f.get_name()][0]
    assert v == 10


def test_diff(es):
    value = IdentityFeature(es['log']['value'])
    customer_id_feat = \
        DirectFeature(base_feature=es['sessions']['customer_id'],
                      child_entity=es['log'])
    diff1 = Diff(value)
    diff2 = Diff(value, es['log']['session_id'])
    diff3 = Diff(value, customer_id_feat)

    pandas_backend = PandasBackend(es, [diff1, diff2, diff3])
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)

    val1 = df[diff1.get_name()].values.tolist()
    val2 = df[diff2.get_name()].values.tolist()
    val3 = df[diff3.get_name()].values.tolist()
    correct_vals1 = [np.nan, 5, 5, 5, 5, -20, 1, 1, 1, -3, 0, 5, -5, 7, 7]
    correct_vals2 = [np.nan, 5, 5, 5, 5, np.nan, 1, 1, 1, np.nan, np.nan, 5, np.nan, 7, 7]
    correct_vals3 = [np.nan, 5, 5, 5, 5, -20, 1, 1, 1, -3, np.nan, 5, -5, 7, 7]
    for i, v in enumerate(val1):
        if np.isnan(v):
            assert (np.isnan(correct_vals1[i]))
        else:
            assert v == correct_vals1[i]
        v2 = val2[i]
        if np.isnan(v2):
            assert (np.isnan(correct_vals2[i]))
        else:
            assert v2 == correct_vals2[i]
        v3 = val3[i]
        if np.isnan(v3):
            assert (np.isnan(correct_vals3[i]))
        else:
            assert v3 == correct_vals3[i]


def test_compare_of_identity(es):
    to_test = [(Compare.EQ, [False, False, True, False]),
               (Compare.NE, [True, True, False, True]),
               (Compare.LT, [True, True, False, False]),
               (Compare.LE, [True, True, True, False]),
               (Compare.GT, [False, False, False, True]),
               (Compare.GE, [False, False, True, True])]

    features = []
    for test in to_test:
        features.append(Compare(es['log']['value'], test[0], 10))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2, 3],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_compare_of_direct(es):
    log_rating = DirectFeature(base_feature=es['products']['rating'],
                               child_entity=es['log'])
    to_test = [(Compare.EQ, [False, False, False, False]),
               (Compare.NE, [True, True, True, True]),
               (Compare.LT, [False, False, False, True]),
               (Compare.LE, [False, False, False, True]),
               (Compare.GT, [True, True, True, False]),
               (Compare.GE, [True, True, True, False])]

    features = []
    for test in to_test:
        features.append(Compare(log_rating, test[0], 4.5))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2, 3],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_compare_of_transform(es):
    day = Day(es['log']['datetime'])
    to_test = [(Compare.EQ, [False, True]),
               (Compare.NE, [True, False]),
               (Compare.LT, [True, False]),
               (Compare.LE, [True, True]),
               (Compare.GT, [False, False]),
               (Compare.GE, [False, True])]

    features = []
    for test in to_test:
        features.append(Compare(day, test[0], 10))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 14],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_compare_of_agg(es):
    count_logs = Count(base_feature=es['log']['id'],
                       parent_entity=es['sessions'])

    to_test = [(Compare.EQ, [False, False, False, True]),
               (Compare.NE, [True, True, True, False]),
               (Compare.LT, [False, False, True, False]),
               (Compare.LE, [False, False, True, True]),
               (Compare.GT, [True, True, False, False]),
               (Compare.GE, [True, True, False, True])]

    features = []
    for test in to_test:
        features.append(Compare(count_logs, test[0], 2))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2, 3],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_arithmetic_of_val(es):
    to_test = [(Add, [2, 3, 4, 5], [2, 3, 3, 2]),
               (Subtract, [-2, -1, 0, 1], [2, 1, 1, 2]),
               (Multiply, [0, 2, 4, 6], [0, 2, 2, 0]),
               (Divide, [0, 0.5, 1, 1.5], [np.inf, 2, 2, np.inf],
                                          [np.nan, np.inf, np.inf, np.inf])]

    features = []
    session = es['sessions']
    for test in to_test:
        features.append(test[0](session['id'], 2))
        features.append(test[0](2, session['device_type']))

    features.append(Divide(session['id'], 0))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2, 3],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[2 * i].get_name()].values.tolist()
        assert v == test[1]
        v = df[features[2 * i + 1].get_name()].values.tolist()
        assert v == test[2]

    test = to_test[-1][-1]
    v = df[features[-1].get_name()].values.tolist()
    assert (np.isnan(v[0]))
    assert v[1:] == test[1:]


def test_arithmetic_two_vals_fails(es):
    with pytest.raises(ValueError):
        Add(2, 2)


def test_arithmetic_of_identity(es):
    to_test = [(Add, [0, 2, 3, 3]),
               (Subtract, [0, 0, 1, 3]),
               (Multiply, [0, 1, 2, 0]),
               (Divide, [np.nan, 1, 2, np.inf])]

    features = []
    session = es['sessions']
    for test in to_test:
        features.append(test[0](session['id'], session['device_type']))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2, 3],
                                               time_last=None)

    for i, test in enumerate(to_test[:-1]):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]
    i, test = 3, to_test[-1]
    v = df[features[i].get_name()].values.tolist()
    assert (np.isnan(v[0]))
    assert v[1:] == test[1][1:]


def test_arithmetic_of_direct(es):
    rating = es['products']['rating']
    log_rating = DirectFeature(base_feature=rating,
                               child_entity=es['log'])
    customer_age = es['customers']['age']
    session_age = DirectFeature(base_feature=customer_age,
                                child_entity=es['sessions'])
    log_age = DirectFeature(base_feature=session_age,
                            child_entity=es['log'])

    to_test = [(Add, [38, 37, 37.5, 37.5]),
               (Subtract, [28, 29, 28.5, 28.5]),
               (Multiply, [165, 132, 148.5, 148.5]),
               (Divide, [6.6, 8.25, 22. / 3, 22. / 3])]

    features = []
    for test in to_test:
        features.append(test[0](log_age, log_rating))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5, 7],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_arithmetic_of_transform(es):
    hour = Hour(es['log']['datetime'])
    day = Day(es['log']['datetime'])

    to_test = [(Add, [19, 19, 19, 19]),
               (Subtract, [-1, -1, -1, -1]),
               (Multiply, [90, 90, 90, 90]),
               (Divide, [.9, .9, .9, .9])]

    features = []
    for test in to_test:
        features.append(test[0](day, hour))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5, 7],
                                               time_last=None)
    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_not_feature(es):
    likes_ice_cream = es['customers']['loves_ice_cream']
    not_feat = Not(likes_ice_cream)
    features = [not_feat]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1],
                                               time_last=None)
    v = df[not_feat.get_name()].values
    assert not v[0]
    assert v[1]


def test_arithmetic_of_agg(es):
    customer_id_feat = es['customers']['id']
    store_id_feat = es['stores']['id']
    count_customer = Count(base_feature=customer_id_feat,
                           parent_entity=es['regions'])
    count_stores = Count(base_feature=store_id_feat,
                         parent_entity=es['regions'])
    to_test = [(Add, [6, 2]),
               (Subtract, [0, -2]),
               (Multiply, [9, 0]),
               (Divide, [1, 0])]

    features = []
    for test in to_test:
        features.append(test[0](count_customer, count_stores))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=['United States', 'Mexico'],
                                               time_last=None)

    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_cum_sum(es):
    log_value_feat = es['log']['value']
    cum_sum = CumSum(log_value_feat, es['log']['session_id'])
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    cum_sum_values = [0, 5, 15, 30, 50, 0, 1, 3, 6, 0, 0, 5, 0, 7, 21]
    for i, v in enumerate(cum_sum_values):
        assert v == cvalues[i]


def test_cum_min(es):
    log_value_feat = es['log']['value']
    cum_min = CumMin(log_value_feat, es['log']['session_id'])
    features = [cum_min]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_min.get_name()].values
    assert len(cvalues) == 15
    cum_min_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i, v in enumerate(cum_min_values):
        assert v == cvalues[i]


def test_cum_max(es):
    log_value_feat = es['log']['value']
    cum_max = CumMax(log_value_feat, es['log']['session_id'])
    features = [cum_max]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_max.get_name()].values
    assert len(cvalues) == 15
    cum_max_values = [0, 5, 10, 15, 20, 0, 1, 2, 3, 0, 0, 5, 0, 7, 14]
    for i, v in enumerate(cum_max_values):
        assert v == cvalues[i]


def test_cum_sum_use_previous(es):
    log_value_feat = es['log']['value']
    cum_sum = CumSum(log_value_feat, es['log']['session_id'],
                     use_previous=Timedelta(3, 'observations',
                                            entity=es['log']))
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    cum_sum_values = [0, 5, 15, 30, 45, 0, 1, 3, 6, 0, 0, 5, 0, 7, 21]
    for i, v in enumerate(cum_sum_values):
        assert v == cvalues[i]


def test_cum_sum_use_previous_integer_time(int_es):
    es = int_es

    log_value_feat = es['log']['value']
    with pytest.raises(AssertionError):
        CumSum(log_value_feat, es['log']['session_id'],
               use_previous=Timedelta(3, 'm'))

    cum_sum = CumSum(log_value_feat, es['log']['session_id'],
                     use_previous=Timedelta(3, 'observations',
                                            entity=es['log']))
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    cum_sum_values = [0, 5, 15, 30, 45, 0, 1, 3, 6, 0, 0, 5, 0, 7, 21]
    for i, v in enumerate(cum_sum_values):
        assert v == cvalues[i]


def test_cum_sum_where(es):
    log_value_feat = es['log']['value']
    compare_feat = Compare(log_value_feat, '>', 3)
    cum_sum = CumSum(log_value_feat, es['log']['session_id'],
                     where=compare_feat)
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    cum_sum_values = [np.nan, 5, 15, 30, 50, np.nan, np.nan,
                      np.nan, np.nan, np.nan, np.nan, 5, np.nan, 7, 21]
    for i, v in enumerate(cum_sum_values):
        if not np.isnan(v):
            assert v == cvalues[i]
        else:
            assert (np.isnan(cvalues[i]))


def test_cum_sum_use_previous_and_where(es):
    log_value_feat = es['log']['value']
    compare_feat = Compare(log_value_feat, '>', 3)
    cum_sum = CumSum(log_value_feat, es['log']['session_id'],
                     where=compare_feat,
                     use_previous=Timedelta(3, 'observations',
                                            entity=es['log']))
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cum_sum_values = [np.nan, 5, 15, 30, 45, np.nan, np.nan,
                      np.nan, np.nan, np.nan, np.nan, 5, np.nan, 7, 21]
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    for i, v in enumerate(cum_sum_values):
        if not np.isnan(v):
            assert v == cvalues[i]
        else:
            assert (np.isnan(cvalues[i]))


def _test_cum_sum_group_on_nan(es):
    log_value_feat = es['log']['value']
    es['log']._get_dataframe()['product_id'] = ['coke zero'] * 3 + ['car'] * 2 + ['toothpaste'] * 3 + ['brown bag'] * 2 + ['shoes'] + [np.nan] * 4 + ['coke_zero'] * 2
    cum_sum = CumSum(log_value_feat, es['log']['product_id'])
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    cum_sum_values = [0, 5, 15, 15, 35, 0, 1, 3, 3, 3, 0, np.nan, np.nan, np.nan, np.nan]
    for i, v in enumerate(cum_sum_values):
        if np.isnan(v):
            assert (np.isnan(cvalues[i]))
        else:
            assert v == cvalues[i]


def test_cum_sum_on_direct_feat(es):
    log_value_feat = es['log']['value']
    customer_id_feat = \
        DirectFeature(base_feature=es['sessions']['customer_id'],
                      child_entity=es['log'])
    cum_sum = CumSum(log_value_feat, customer_id_feat)
    features = [cum_sum]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_sum.get_name()].values
    assert len(cvalues) == 15
    cum_sum_values = [0, 5, 15, 30, 50, 50, 51, 53, 56, 56, 0, 5, 5, 12, 26]
    for i, v in enumerate(cum_sum_values):
        assert v == cvalues[i]


def test_cum_mean(es):
    log_value_feat = es['log']['value']
    cum_mean = CumMean(log_value_feat, es['log']['session_id'])
    features = [cum_mean]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_mean.get_name()].values
    assert len(cvalues) == 15
    cum_mean_values = [0, 2.5, 5, 7.5, 10, 0, .5, 1, 1.5, 0, 0, 2.5, 0, 3.5, 7]
    for i, v in enumerate(cum_mean_values):
        assert v == cvalues[i]


def test_cum_mean_use_previous(es):
    log_value_feat = es['log']['value']
    cum_mean = CumMean(log_value_feat, es['log']['session_id'],
                       use_previous=Timedelta(3, 'observations',
                                              entity=es['log']))
    features = [cum_mean]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_mean.get_name()].values
    assert len(cvalues) == 15
    cum_mean_values = [0, 2.5, 5, 10, 15, 0, .5, 1, 2, 0, 0, 2.5, 0, 3.5, 7]
    for i, v in enumerate(cum_mean_values):
        assert v == cvalues[i]


def test_cum_mean_where(es):
    log_value_feat = es['log']['value']
    compare_feat = Compare(log_value_feat, '>', 3)
    cum_mean = CumMean(log_value_feat, es['log']['session_id'],
                       where=compare_feat)
    features = [cum_mean]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_mean.get_name()].values
    assert len(cvalues) == 15
    cum_mean_values = [np.nan, 5, 7.5, 10, 12.5, np.nan, np.nan,
                       np.nan, np.nan, np.nan, np.nan, 5, np.nan, 7, 10.5]

    for i, v in enumerate(cum_mean_values):
        if not np.isnan(v):
            assert v == cvalues[i]
        else:
            assert (np.isnan(cvalues[i]))


def test_cum_mean_use_previous_and_where(es):
    log_value_feat = es['log']['value']
    compare_feat = Compare(log_value_feat, '>', 3)
    # todo should this be cummean?
    cum_mean = CumSum(log_value_feat, es['log']['session_id'],
                      where=compare_feat,
                      use_previous=Timedelta(3, 'observations',
                                             entity=es['log']))
    features = [cum_mean]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cum_mean_values = [np.nan, 5, 7.5, 10, 15, np.nan, np.nan,
                       np.nan, np.nan, np.nan, np.nan, 5, np.nan, 7, 10.5]
    cvalues = df[cum_mean.get_name()].values
    assert len(cvalues) == 15
    cum_mean_values = []
    for i, v in enumerate(cum_mean_values):
        if not np.isnan(v):
            assert v == cvalues[i]
        else:
            assert (np.isnan(cvalues[i]))


def test_cum_count(es):
    log_value_feat = es['log']['value']
    cum_count = CumCount(log_value_feat, es['log']['session_id'])
    features = [cum_count]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(15),
                                               time_last=None)
    cvalues = df[cum_count.get_name()].values
    assert len(cvalues) == 15
    cum_count_values = [1, 2, 3, 4, 5, 1, 2, 3, 4, 1, 1, 2, 1, 2, 3]
    for i, v in enumerate(cum_count_values):
        assert v == cvalues[i]


def test_arithmetic(es):
    hour = Hour(es['log']['datetime'])
    day = Day(es['log']['datetime'])

    to_test = [(Add, [19, 19, 19, 19]),
               (Subtract, [-1, -1, -1, -1]),
               (Multiply, [90, 90, 90, 90]),
               (Divide, [.9, .9, .9, .9])]

    features = []
    features.append(day + hour)
    features.append(day - hour)
    features.append(day * hour)
    features.append(day / hour)

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5, 7],
                                               time_last=None)
    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test[1]


def test_overrides(es):
    hour = Hour(es['log']['datetime'])
    day = Day(es['log']['datetime'])

    feats = [Add, Subtract, Multiply, Divide,
             Mod, And, Or]
    compare_ops = ['>', '<', '=', '!=',
                   '>=', '<=']
    assert Negate(hour).hash() == (-hour).hash()

    compares = [(hour, hour),
                (hour, day),
                (day, 2)]
    overrides = [
        hour + hour,
        hour - hour,
        hour * hour,
        hour / hour,
        hour % hour,
        hour & hour,
        hour | hour,
        hour > hour,
        hour < hour,
        hour == hour,
        hour != hour,
        hour >= hour,
        hour <= hour,

        hour + day,
        hour - day,
        hour * day,
        hour / day,
        hour % day,
        hour & day,
        hour | day,
        hour > day,
        hour < day,
        hour == day,
        hour != day,
        hour >= day,
        hour <= day,

        day + 2,
        day - 2,
        day * 2,
        day / 2,
        day % 2,
        day & 2,
        day | 2,
        day > 2,
        day < 2,
        day == 2,
        day != 2,
        day >= 2,
        day <= 2,
    ]

    i = 0
    for left, right in compares:
        for feat in feats:
            f = feat(left, right)
            o = overrides[i]
            assert o.hash() == f.hash()
            i += 1

        for compare_op in compare_ops:
            f = Compare(left, compare_op, right)
            o = overrides[i]
            assert o.hash() == f.hash()
            i += 1

    our_reverse_overrides = [
        2 + day,
        2 - day,
        2 * day,
        2 / day,
        2 & day,
        2 | day]
    i = 0
    for feat in feats:
        if feat != Mod:
            f = feat(2, day)
            o = our_reverse_overrides[i]
            assert o.hash() == f.hash()
            i += 1

    python_reverse_overrides = [
        2 < day,
        2 > day,
        2 == day,
        2 != day,
        2 <= day,
        2 >= day]
    i = 0
    for compare_op in compare_ops:
        f = Compare(day, compare_op, 2)
        o = python_reverse_overrides[i]
        assert o.hash() == f.hash()
        i += 1


def test_override_boolean(es):
    count = Count(es['log']['value'], es['sessions'])
    count_lo = Compare(count, '>', 1)
    count_hi = Compare(count, '<', 10)

    to_test = [[True, True, True],
               [True, True, False],
               [False, False, True]]

    features = []
    features.append(count_lo.OR(count_hi))
    features.append(count_lo.AND(count_hi))
    features.append(~(count_lo.AND(count_hi)))

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2],
                                               time_last=None)
    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test


def test_override_cmp_from_variable(es):
    count_lo = IdentityFeature(es['log']['value']) > 1

    to_test = [False, True, True]

    features = [count_lo]

    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2],
                                               time_last=None)
    v = df[count_lo.get_name()].values.tolist()
    for i, test in enumerate(to_test):
        assert v[i] == test


def test_override_cmp(es):
    count = Count(es['log']['value'], es['sessions'])
    _sum = Sum(es['log']['value'], es['sessions'])
    gt_lo = count > 1
    gt_other = count > _sum
    ge_lo = count >= 1
    ge_other = count >= _sum
    lt_hi = count < 10
    lt_other = count < _sum
    le_hi = count <= 10
    le_other = count <= _sum
    ne_lo = count != 1
    ne_other = count != _sum

    to_test = [[True, True, False],
               [False, False, True],
               [True, True, True],
               [False, False, True],
               [True, True, True],
               [True, True, False],
               [True, True, True],
               [True, True, False]]
    features = [gt_lo, gt_other, ge_lo, ge_other, lt_hi,
                lt_other, le_hi, le_other, ne_lo, ne_other]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1, 2],
                                               time_last=None)
    for i, test in enumerate(to_test):
        v = df[features[i].get_name()].values.tolist()
        assert v == test


@pytest.mark.longtest
@pytest.mark.requires_training_data
def test_word2vec_feat(es):
    # pretty good setting: 50 clusters, batch size of 500
    w2vfeat = Word2VecCluster(es['log']['comments'],
                              num_clusters=10,
                              random_state=1)
    features = [w2vfeat]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(17),
                                               time_last=None)
    true_values = [
        [96, 103, 0, 0, 12, 0, 62, 1, 12, 207],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [34, 215, 1, 0, 13, 72, 153, 2, 0, 190],
        [83, 389, 0, 0, 27, 81, 196, 12, 0, 399],
        [145, 311, 0, 0, 56, 0, 94, 9, 0, 594],
        [28, 28, 0, 0, 9, 0, 11, 5, 0, 76],
        [15, 36, 0, 0, 10, 0, 11, 3, 0, 81],
        [7, 19, 0, 0, 4, 0, 11, 2, 0, 32],
        [22, 72, 0, 0, 12, 0, 36, 2, 0, 81],
        [91, 315, 0, 20, 32, 0, 163, 105, 0, 375],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [5, 17, 0, 0, 4, 0, 3, 0, 0, 15],
        [2, 4, 0, 0, 0, 0, 3, 0, 0, 8],
    ]
    true_values = [np.array(r) for r in true_values]
    for i, values in df[w2vfeat.get_name()].iteritems():
        true_row = true_values[i]
        assert np.array_equal(values, true_row) is True


@pytest.mark.longtest
@pytest.mark.requires_training_data
def test_word2vec_feat_obey_time_bounds(es):
    w2vfeat = Word2VecCluster(es['log']['comments'],
                              num_clusters=10,
                              random_state=1,
                              obey_time_bounds_in_training=True)

    time_last = datetime(2011, 4, 10, 10, 30, 59)
    features = [w2vfeat]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(instance_ids=range(17),
                                               time_last=time_last)
    true_values = [
        np.array([10, 153, 5, 0, 34, 0, 166, 92, 8, 25]),
        np.array([0, 0, 1, 0, 1, 0, 0, 1, 0, 0]),
        np.array([0, 0, 1, 0, 1, 0, 0, 1, 0, 0]),
        np.array([16, 356, 44, 16, 25, 0, 66, 116, 11, 30]),
        np.array([14, 646, 52, 0, 53, 0, 127, 239, 12, 44]),
        np.array([14, 363, 54, 0, 120, 45, 179, 293, 80, 61]),
        np.array([2, 42, 15, 0, 28, 8, 25, 28, 5, 4]),
        np.array([2, 42, 7, 0, 17, 6, 26, 39, 4, 13]),
        np.array([2, 28, 3, 0, 6, 0, 4, 24, 3, 5]),
        np.array([3, 105, 13, 0, 18, 0, 22, 53, 0, 11]),
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    ]
    for i, values in df[w2vfeat.get_name()].iteritems():
        true_row = true_values[i]
        if type(true_row) != np.ndarray:
            assert np.isnan(values)
        else:
            assert np.array_equal(values, true_row) is True


def test_isin_feat(es):
    isin = IsIn(es['log']['product_id'], ["toothpaste", "coke zero"])
    features = [isin]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(range(8), None)
    true = [True, True, True, False, False, True, True, True]
    v = df[isin.get_name()].values.tolist()
    assert true == v


def test_isin_feat_other_syntax(es):
    isin = Feature(es['log']['product_id']).isin(["toothpaste", "coke zero"])
    features = [isin]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(range(8), None)
    true = [True, True, True, False, False, True, True, True]
    v = df[isin.get_name()].values.tolist()
    assert true == v


def test_isin_feat_other_syntax_int(es):
    isin = Feature(es['log']['value']).isin([5, 10])
    features = [isin]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(range(8), None)
    true = [False, True, True, False, False, False, False, False]
    v = df[isin.get_name()].values.tolist()
    assert true == v


def test_like_feat(es):
    like = Like(es['log']['product_id'], "coke")
    features = [like]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(range(5), None)
    true = [True, True, True, False, False]
    v = df[like.get_name()].values.tolist()
    assert true == v


def test_like_feat_other_syntax(es):
    like = Feature(es['log']['product_id']).LIKE("coke")
    features = [like]
    pandas_backend = PandasBackend(es, features)
    df = pandas_backend.calculate_all_features(range(5), None)
    true = [True, True, True, False, False]
    v = df[like.get_name()].values.tolist()
    assert true == v
