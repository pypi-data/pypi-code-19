import numpy as np
import pytest

from featuretools.synthesis.deep_feature_synthesis import DeepFeatureSynthesis
from featuretools.primitives import Count, Mean, Sum, ALL_AGG_FEATS
from featuretools.primitives import Feature, SlidingWindow, SlidingMean
from featuretools.variable_types import Discrete, Numeric, Categorical, Ordinal, Boolean, Text, Datetime
from ..testing_utils import make_ecommerce_entityset, feature_with_name
from featuretools import Timedelta
from featuretools.computational_backends import PandasBackend
from datetime import datetime


@pytest.fixture(scope='module')
def es():
    return make_ecommerce_entityset()


@pytest.fixture
def child_entity(es):
    return es['customers']


@pytest.fixture
def grandchild_entity(es):
    return es['sessions']


@pytest.fixture
def child(es, child_entity):
    return Count(base_feature=es['sessions']['id'],
                 parent_entity=child_entity)


@pytest.fixture
def parent_class():
    return Mean


@pytest.fixture
def parent_entity(es):
    return es['regions']


@pytest.fixture
def parent(parent_class, parent_entity, child):
    return make_parent_instance(parent_class,
                                parent_entity, child)


def make_parent_instance(parent_class, parent_entity, base_feature,
                         where=None):
    return parent_class(base_feature, parent_entity, where=where)


def test_get_depth(es):
    log_id_feat = es['log']['id']
    customer_id_feat = es['customers']['id']
    count_logs = Count(base_feature=log_id_feat,
                       parent_entity=es['sessions'])
    sum_count_logs = Sum(base_feature=count_logs,
                         parent_entity=es['customers'])
    num_logs_greater_than_5 = sum_count_logs > 5
    count_customers = Count(base_feature=customer_id_feat,
                            parent_entity=es['regions'],
                            where=num_logs_greater_than_5)
    num_customers_region = Feature(count_customers, es["customers"])

    depth = num_customers_region._get_depth()
    assert depth == 4


def test_makes_rcount(es):
    dfs = DeepFeatureSynthesis(target_entity_id='sessions',
                               entityset=es,
                               filters=[],
                               agg_primitives=[Count],
                               trans_primitives=[])

    features = dfs.build_features()
    assert feature_with_name(features, 'device_type')
    assert feature_with_name(features, 'customer_id')
    assert feature_with_name(features, 'customers.region_id')
    assert feature_with_name(features, 'customers.age')
    assert feature_with_name(features, 'COUNT(log)')
    assert feature_with_name(features, 'customers.COUNT(sessions)')
    assert feature_with_name(features, 'customers.regions.language')
    assert feature_with_name(features, 'customers.COUNT(log)')


def test_check_feature_signature(es, child, parent):
    mean = parent
    assert mean._check_feature_signature()
    boolean = child > 3
    mean = make_parent_instance(Mean, es['regions'],
                                child, where=boolean)
    assert mean._check_feature_signature()


def test_base_of_and_stack_on_heuristic(es, parent, parent_entity, child):
    parent.stack_on = []
    child.base_of = []
    assert not (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = []
    child.base_of = None
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = []
    child.base_of = ['mean']
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = None
    child.base_of = []
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = None
    child.base_of = None
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = None
    child.base_of = ['mean']
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = ['count']
    child.base_of = []
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = ['count']
    child.base_of = None
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = ['count']
    child.base_of = ['mean']
    assert (parent.can_apply(parent_entity, 'customers'))


def test_stack_on_self(es, parent, child, parent_entity):
    # test stacks on self
    parent.stack_on = []
    child.base_of = []
    parent.stacks_on_self = False
    child.stacks_on_self = False
    parent.function_name = 'count'
    assert not parent.can_apply(parent_entity, 'customers')

    parent.stacks_on_self = True
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = []
    child.base_of = []
    parent.function_name = 'mean'
    child.function_name = 'mean'
    parent.stacks_on_self = False
    assert not (parent.can_apply(parent_entity, 'customers'))

    parent.stacks_on_self = True
    assert (parent.can_apply(parent_entity, 'customers'))

    parent.stack_on = None
    parent.stacks_on_self = False
    assert not parent.can_apply(parent_entity, 'customers')


def test_max_depth_heuristic(es, parent_class, parent_entity, parent):
    grandparent = make_parent_instance(parent_class, parent_entity,
                                       parent)
    for f in [parent, grandparent]:
        f.stack_on = ['child']
        f.stacks_on_self = True
        f.base_of = ['parent']
        f.apply_to = [(Numeric,)]
        f.max_stack_depth = 2

    assert parent.can_apply(parent_entity, 'customers')
    assert not grandparent.can_apply(parent_entity, 'customers')

    grandparent.max_stack_depth = 3
    assert grandparent.can_apply(parent_entity, 'customers')


def test_init_and_name(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    categorical_identity_feature = log['product_id']
    ordinal_identity_feature = log['priority_level']
    boolean_identity_feature = log['purchased']
    text_identity_feature = log['comments']
    datetime_identity_feature = log['datetime']

    for agg_feat in ALL_AGG_FEATS:
        parent_entity = session
        if (Numeric,) in agg_feat.apply_to:
            feat = numeric_identity_feature
        elif (Discrete,) in agg_feat.apply_to:
            feat = categorical_identity_feature
        elif (Categorical,) in agg_feat.apply_to:
            feat = categorical_identity_feature
        elif (Ordinal,) in agg_feat.apply_to:
            feat = ordinal_identity_feature
        elif (Boolean,) in agg_feat.apply_to:
            feat = boolean_identity_feature
        elif (Text,) in agg_feat.apply_to:
            feat = text_identity_feature
        elif (Datetime,) in agg_feat.apply_to:
            feat = datetime_identity_feature
        instance = agg_feat(base_feature=feat, parent_entity=parent_entity)
        instance.get_name()


def test_init_and_name_sliding_window(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(10, 'd')
    gap = Timedelta(-1, 'd')
    window_size = Timedelta(2, 'd')
    with pytest.raises(AssertionError):
        instance = SlidingWindow("mean", base_feature=numeric_identity_feature,
                                 parent_entity=session)
        instance.get_name()
    instance = SlidingWindow("mean", base_feature=numeric_identity_feature,
                             parent_entity=session,
                             use_previous=use_previous,
                             gap=gap,
                             window_size=window_size)
    instance.get_name()


def test_sliding_window_observations(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(10, 'observations', log)
    gap = Timedelta(0, 'observations', log)
    window_size = Timedelta(2, 'observations', log)

    sl = SlidingMean(base_feature=numeric_identity_feature,
                     parent_entity=session,
                     use_previous=use_previous,
                     gap=gap,
                     window_size=window_size)

    true_values = [[]]

    pandas_backend = PandasBackend(es, [sl])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5],
                                               time_last=datetime(2011, 4, 10, 11, 10, 6))
    true_values = [
        [np.nan, np.nan, 0, 7.5, 17.5],
        [np.nan, np.nan, np.nan, np.nan, 2.5],
        [np.nan] * 5
    ]
    v = df[sl.get_name()].values.tolist()
    for i, values in enumerate(v):
        true = true_values[i]
        assert len(values) == len(true)
        assert all((np.isnan(true[j]) and np.isnan(values[j])) or
                   true[j] == values[j] for j in xrange(len(values)))


def test_sliding_window_observations_neg_gap(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(10, 'observations', log)
    gap = Timedelta(-1, 'observations', log)
    window_size = Timedelta(3, 'observations', log)

    sl = SlidingMean(base_feature=numeric_identity_feature,
                     parent_entity=session,
                     use_previous=use_previous,
                     gap=gap,
                     window_size=window_size)

    true_values = [[]]

    pandas_backend = PandasBackend(es, [sl])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5, 7],
                                               time_last=datetime(2011, 4, 10, 11, 10, 6))
    true_values = [
        [np.nan] * 2 + [0, 5, 15],
        [np.nan] * 4 + [2.5],
        [np.nan] * 5,
        [np.nan] * 5
    ]
    v = df[sl.get_name()].values.tolist()
    for i, values in enumerate(v):
        true = true_values[i]
        assert len(values) == len(true)
        assert all((np.isnan(true[j]) and np.isnan(values[j])) or
                   true[j] == values[j] for j in xrange(len(values)))


def test_sliding_window_observations_neg_gap_2(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(10, 'observations', log)
    gap = Timedelta(-3, 'observations', log)
    window_size = Timedelta(4, 'observations', log)

    sl = SlidingMean(base_feature=numeric_identity_feature,
                     parent_entity=session,
                     use_previous=use_previous,
                     gap=gap,
                     window_size=window_size)

    true_values = [[]]

    pandas_backend = PandasBackend(es, [sl])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 1],
                                               time_last=datetime(2011, 4, 10, 11, 10, 6))
    true_values = [
        [np.nan] * 5 + [0, 2.5, 5, 7.5, 12.5],
        [np.nan] * 6 + [0, 0.5, 1, 1.5],
    ]
    v = df[sl.get_name()].values.tolist()
    for i, values in enumerate(v):
        true = true_values[i]
        assert len(values) == len(true)
        assert all((np.isnan(true[j]) and np.isnan(values[j])) or
                   true[j] == values[j] for j in xrange(len(values)))


def test_sliding_window_observations_gap(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(10, 'observations', log)
    gap = Timedelta(2, 'observations', log)
    window_size = Timedelta(2, 'observations', log)

    sl = SlidingMean(base_feature=numeric_identity_feature,
                     parent_entity=session,
                     use_previous=use_previous,
                     gap=gap,
                     window_size=window_size)

    true_values = [[]]

    pandas_backend = PandasBackend(es, [sl])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5, 7],
                                               time_last=datetime(2011, 4, 10, 11, 10, 6))
    true_values = [
        [np.nan, 0, 17.5],
        [np.nan, np.nan, 2.5],
        [np.nan] * 3,
        [np.nan] * 3
    ]
    v = df[sl.get_name()].values.tolist()
    for i, values in enumerate(v):
        true = true_values[i]
        assert len(values) == len(true)
        assert all((np.isnan(true[j]) and np.isnan(values[j])) or
                   true[j] == values[j] for j in xrange(len(values)))


def test_sliding_window_time_units(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(1, 'm')
    gap = Timedelta(0, 's')
    window_size = Timedelta(10, 's')

    sl = SlidingMean(base_feature=numeric_identity_feature,
                     parent_entity=session,
                     use_previous=use_previous,
                     gap=gap,
                     window_size=window_size)

    true_values = [[]]

    pandas_backend = PandasBackend(es, [sl])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5, 7],
                                               time_last=datetime(2011, 4, 9, 10, 30, 30))
    true_values = [
        [np.nan] * 4 + [0, 7.5, 17.5],
        [np.nan] * 7,
        [np.nan] * 7,
        [np.nan] * 7
    ]
    v = df[sl.get_name()].values.tolist()
    for i, values in enumerate(v):
        true = true_values[i]
        assert len(values) == len(true)
        assert all((np.isnan(true[j]) and np.isnan(values[j])) or
                   true[j] == values[j] for j in xrange(len(values)))


def test_sliding_window_time_units_gap(es):
    session = es['sessions']
    log = es['log']
    numeric_identity_feature = log['value']
    use_previous = Timedelta(1, 'm')
    gap = Timedelta(3, 's')
    window_size = Timedelta(10, 's')

    sl = SlidingMean(base_feature=numeric_identity_feature,
                     parent_entity=session,
                     use_previous=use_previous,
                     gap=gap,
                     window_size=window_size)

    true_values = [[]]

    pandas_backend = PandasBackend(es, [sl])
    df = pandas_backend.calculate_all_features(instance_ids=[0, 3, 5],
                                               time_last=datetime(2011, 4, 9, 10, 30, 30))
    true_values = [
        [np.nan] * 3 + [5, 17.5],
        [np.nan] * 5,
        [np.nan] * 5
    ]
    v = df[sl.get_name()].values.tolist()
    for i, values in enumerate(v):
        true = true_values[i]
        assert len(values) == len(true)
        assert all((np.isnan(true[j]) and np.isnan(values[j])) or
                   true[j] == values[j] for j in xrange(len(values)))
