import pytest
from featuretools.primitives import IdentityFeature, Sum
from ..testing_utils import make_ecommerce_entityset
from featuretools.utils.gen_utils import getsize


@pytest.fixture(scope='module')
def es():
    return make_ecommerce_entityset()


def test_copy_features_does_not_copy_entityset(es):
    agg = Sum(es['log']['value'], es['sessions'])
    agg_where = Sum(es['log']['value'], es['sessions'],
                    where=IdentityFeature(es['log']['value'])==2)
    agg_use_previous = Sum(es['log']['value'], es['sessions'],
                           use_previous='4 days')
    agg_use_previous_where = Sum(es['log']['value'], es['sessions'],
                                 where=IdentityFeature(es['log']['value'])==2,
                                 use_previous='4 days')
    features = [agg, agg_where, agg_use_previous, agg_use_previous_where]
    in_memory_size = getsize(locals())
    copied = [f.copy() for f in features]
    new_in_memory_size = getsize(locals())
    assert new_in_memory_size < 2 * in_memory_size

    for f, c in zip(features, copied):
        assert f.entityset
        assert c.entityset
        assert id(f.entityset) == id(c.entityset)
        if f.where:
            assert c.where
            assert id(f.where.entityset) == id(c.where.entityset)
        for bf, bf_c in zip(f.base_features, c.base_features):
            assert id(bf.entityset) == id(bf_c.entityset)
            if bf.where:
                assert bf_c.where
                assert id(bf.where.entityset) == id(bf_c.where.entityset)
