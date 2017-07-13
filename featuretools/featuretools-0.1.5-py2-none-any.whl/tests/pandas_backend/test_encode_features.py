from featuretools.synthesis import encode_features
from ..testing_utils import make_ecommerce_entityset
from featuretools.primitives import IdentityFeature
from featuretools import calculate_feature_matrix

from datetime import datetime
import pytest

@pytest.fixture(scope='module')
def entityset():
    return make_ecommerce_entityset()

def test_encodes_features(entityset):
    f1 = IdentityFeature(entityset["log"]["product_id"])
    f2 = IdentityFeature(entityset["log"]["purchased"])
    f3 = IdentityFeature(entityset["log"]["value"])

    features = [f1, f2, f3]
    feature_matrix = calculate_feature_matrix(features, instance_ids=[0, 1, 2, 3, 4, 5])

    features_encoded, feature_matrix_encoded = encode_features(features, feature_matrix)
    assert len(features_encoded) == 6

    features_encoded, feature_matrix_encoded = encode_features(features, feature_matrix, top_n=2)
    assert len(features_encoded) == 5

    features_encoded, feature_matrix_encoded = encode_features(features, feature_matrix,
                                                               include_unknown=False)
    assert len(features_encoded) == 5


def test_inplace_encodes_features(entityset):
    f1 = IdentityFeature(entityset["log"]["product_id"])

    features = [f1]
    feature_matrix = calculate_feature_matrix(features, instance_ids=[0, 1, 2, 3, 4, 5])

    feature_matrix_shape = feature_matrix.shape
    features_encoded, feature_matrix_encoded = encode_features(features, feature_matrix)
    assert feature_matrix_encoded.shape != feature_matrix_shape
    assert feature_matrix.shape == feature_matrix_shape

    # inplace they should be the same
    features_encoded, feature_matrix_encoded = encode_features(features, feature_matrix, inplace=True)
    assert feature_matrix_encoded.shape == feature_matrix.shape
