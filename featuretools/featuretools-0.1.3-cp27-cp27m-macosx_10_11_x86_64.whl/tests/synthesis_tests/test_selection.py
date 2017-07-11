# MAX - I don't think we need this file anymore
# import pytest
# from mock import Mock
# from featuretools.entityset.entity import Entity
# from featuretools.synthesis.feature_selectors import SelectedGroup, MinMaxMeanSelector, SumCountMeanSelector, CompositeSelector
# from featuretools.features import Sum, Mean, Count, Min, Max
# from featuretools.features import FeatureBase, IdentityFeature
# import numpy as np


# @pytest.fixture
# def mean_mock():
#     mean_mock = Mock(spec=Mean)
#     mean_mock.base_features = ["test"]
#     return mean_mock


# @pytest.fixture
# def max_mock():
#     max_mock = Mock(spec=Max)
#     max_mock.base_features = ["test"]
#     return max_mock


# @pytest.fixture
# def min_mock():
#     min_mock = Mock(spec=Min)
#     min_mock.base_features = ["test"]
#     return min_mock


# @pytest.fixture
# def labels():
#     return [True, False, True]


# def test_select_on_single_group(mean_mock, min_mock, max_mock, labels):
#     features = [min_mock, mean_mock, max_mock]
#     feature_matrix = np.array([[1, 2, 3], [2, -4, -9], [3, 8, 27]])
#     mmm = MinMaxMeanSelector(verbose=False)
#     feature_matrix, features = mmm.select(feature_matrix, features, labels)
#     assert min_mock not in features


# # TODO: only passes alone: min feature is being scored as nan
# # def test_select_on_multiple_sets(labels):
# #     mock_entity = Mock(spec=Entity)
# #     mock_entity.id = "test_entity_id"
# #     mock_feature = Mock(spec=IdentityFeature)
# #     mock_feature.entity = mock_entity
# #     mean_mock = Mock(spec=Mean)
# #     mean_mock.base_features = [mock_feature]

# #     min_mock = Mock(spec=Min)
# #     min_mock.base_features = [mock_feature]

# #     max_mock = Mock(spec=Max)
# #     max_mock.base_features = [mock_feature]

# #     sum_mock = Mock(spec=Sum)
# #     sum_mock.base_features = [mock_feature]

# #     count_mock = Mock(spec=Count)
# #     count_mock.base_features = [mock_feature]
# #     count_mock.child_entity = mock_entity
# #     features = [min_mock, mean_mock, max_mock, count_mock, sum_mock]
# #     feature_matrix = np.array([[1, 2, 3, 2, 2], [1, 4, 9, 4.01, 4.1], [1, 8, 27, 8.01, 8.1]])
# #     scm = SumCountMeanSelector()
# #     mmm = MinMaxMeanSelector()
# #     remover = CompositeSelector([scm, mmm], verbose=False)
# #     pdb.set_trace()
# #     feature_matrix, features = remover.select(feature_matrix, features, labels)
# #     assert mean_mock in features
# #     assert sum_mock not in features
# #     assert max_mock in features
# #     assert count_mock in features
# #     assert min_mock in features


# # TODO: doesn't pass for some reason
# def test_group_creation(mean_mock, min_mock, max_mock, labels):
#     mean_mock2 = Mock(spec=Mean)
#     mean_mock2.base_features = ["test2"]
#     max_mock2 = Mock(spec=Max)
#     max_mock2.base_features = ["test2"]
#     min_mock2 = Mock(spec=Min)
#     min_mock2.base_features = ["test2"]
#     lonely_max = Mock(spec=Max)
#     lonely_max.base_features = "lonely_base"
#     mmm = MinMaxMeanSelector(verbose=False)
#     features = [min_mock, mean_mock, max_mock, min_mock2, mean_mock2, max_mock2, lonely_max]
#     groups = mmm._find_groups(features)
#     assert len(groups) == 2


# def test_scoring(mean_mock, min_mock, max_mock, labels):
#     features = [min_mock, mean_mock, max_mock]
#     group = SelectedGroup(2, features)
#     mmm = MinMaxMeanSelector(verbose=False)
#     feature_matrix = np.array([[1, 1, 0], [1, 5, 0], [np.nan, 9, 0]])
#     scored_group = mmm._score_groups([group], feature_matrix, features, labels)[0]
#     assert np.isnan(scored_group.scores[features[0]])

#     assert scored_group.scores[features[1]] == 0.0
#     assert np.isnan(scored_group.scores[features[2]])
