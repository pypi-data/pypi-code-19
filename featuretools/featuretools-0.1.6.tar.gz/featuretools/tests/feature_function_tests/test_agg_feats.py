import pytest

from featuretools.synthesis.deep_feature_synthesis import DeepFeatureSynthesis
from featuretools.primitives import Feature, Count, Mean, Sum, ALL_AGG_FEATS
from featuretools.variable_types import (Discrete, Numeric, Categorical,
                                         Ordinal, Boolean, Text, Datetime)
from ..testing_utils import make_ecommerce_entityset, feature_with_name


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
