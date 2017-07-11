import pytest
from featuretools.primitives import Count, Mode, Feature, DirectFeature, Compare
from featuretools import variable_types
from ..testing_utils import make_ecommerce_entityset
from featuretools.synthesis import dfs_filters as filt


@pytest.fixture(scope='module')
def es():
    return make_ecommerce_entityset()


@pytest.fixture
def session_id_feat(es):
    return Feature(es['sessions']['id'])


@pytest.fixture
def product_id_feat(es):
    return Feature(es['log']['product_id'])


@pytest.fixture
def datetime_feat(es):
    return Feature(es['log']['datetime'])


def test_limit_mode_uniques(es, session_id_feat, product_id_feat, datetime_feat):
    mode_feat = Mode(base_feature=product_id_feat,
                     parent_entity=es['sessions'])

    mode_filter = filt.LimitModeUniques()

    assert mode_filter.is_valid(feature=mode_feat,
                                entity=es['sessions'],
                                target_entity_id='customers')

    # percent_unique is 6/15
    mode_filter = filt.LimitModeUniques(threshold=.3)

    assert not mode_filter.is_valid(feature=mode_feat,
                                    entity=es['sessions'],
                                    target_entity_id='customers')


def test_limit_where_clauses_by_variable_type(es, session_id_feat, product_id_feat, datetime_feat):
    feature = Mode
    child_feature = product_id_feat
    child_entity = es['log']
    where = Compare(product_id_feat, Compare.LT, 3)
    where_filt = filt.LimitWhereClausesByVariableType(variable_types=[variable_types.Categorical])
    assert where_filt.is_valid(feature=feature,
                               child_feature=child_feature,
                               child_entity=child_entity,
                               where=where)
    where_filt = filt.LimitWhereClausesByVariableType(variable_types=[variable_types.Numeric])
    assert not where_filt.is_valid(feature=feature,
                                   child_feature=child_feature,
                                   child_entity=child_entity,
                                   where=where)


def test_limit_where_clauses_by_feature_type(es, session_id_feat, product_id_feat, datetime_feat):
    feature = Mode
    child_feature = product_id_feat
    child_entity = es['log']
    where = Compare(product_id_feat, Compare.LT, 3)
    where_filt = filt.LimitWhereClausesByFeatureType(feature_types=[Mode])
    assert where_filt.is_valid(feature=feature,
                               child_feature=child_feature,
                               child_entity=child_entity,
                               where=where)
    where_filt = filt.LimitWhereClausesByFeatureType(feature_types=[Count])
    assert not where_filt.is_valid(feature=feature,
                                   child_feature=child_feature,
                                   child_entity=child_entity,
                                   where=where)


def test_where_feats_different_than_base_feats(es, session_id_feat, product_id_feat, datetime_feat):
    feature = Mode
    child_feature = product_id_feat
    child_entity = es['log']
    where = Compare(product_id_feat, Compare.LT, 3)
    where_filt = filt.WhereFeatsDifferentThanBaseFeats()
    assert not where_filt.is_valid(feature=feature,
                                   child_feature=child_feature,
                                   child_entity=child_entity,
                                   where=where)

    where = Compare(datetime_feat, Compare.LT, 3)
    where_filt = filt.WhereFeatsDifferentThanBaseFeats()
    assert where_filt.is_valid(feature=feature,
                               child_feature=child_feature,
                               child_entity=child_entity,
                               where=where)


def test_dfeat_where(es, session_id_feat, product_id_feat, datetime_feat):
    child_entity = es['sessions']
    grandchild_feature = product_id_feat
    grandchild_entity = es['log']
    where = Compare(datetime_feat, Compare.LT, 3)
    agg_feature = Mode(grandchild_feature,
                       child_entity,
                       where=where)

    where_filt = filt.DFeatWhere()

    assert not where_filt.is_valid(feature=DirectFeature,
                                   child_feature=agg_feature,
                                   child_entity=child_entity)

    agg_feature = Mode(grandchild_feature,
                       grandchild_entity,
                       where=None)
    assert where_filt.is_valid(feature=DirectFeature,
                               child_feature=agg_feature,
                               child_entity=child_entity)


def test_pre_instance_apply_to(es, session_id_feat, product_id_feat, datetime_feat):
    # should return True before checking child feature or child entity
    dfeat_filter = filt.DFeatWhere()
    assert dfeat_filter.is_valid(feature=Count,
                                 child_feature=None,
                                 child_entity=None)
