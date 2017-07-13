import pytest
from featuretools.synthesis import DeepFeatureSynthesis, dfs
import copy
from featuretools.primitives import (Last, Count, Hour, IdentityFeature,
                                   TransformFeature, AggregationFeature,
                                   Feature, Max, Mean, Min, Sum, Diff,
                                   TimeSincePrevious, CumMean)
from ..testing_utils import make_ecommerce_entityset, feature_with_name
import pandas as pd


@pytest.fixture(scope='module')
def es():
    return make_ecommerce_entityset()


@pytest.fixture(scope='module')
def entities():
    cards_df = pd.DataFrame({"id": [1, 2, 3]})
    transactions_df = pd.DataFrame({"id": [1, 2, 3, 4, 5, 6],
                                    "card_id": [1, 2, 1, 3, 4, 5],
                                    "transaction_time": [10, 12, 15, 20, 21, 20],
                                    "fraud": [True, False, True, False, True, True]})
    entities = {
        "cards": (cards_df, "id"),
        "transactions": (transactions_df, "id", "transaction_time")
    }
    return entities


@pytest.fixture(scope='module')
def relationships():
    return [("cards", "id", "transactions", "card_id")]


class TestDeepFeatureSynthesis(object):
    def test_makes_agg_features(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'LAST(log.value)'))

    def test_only_makes_supplied_agg_feat(self, es):
            kwargs = dict(
                target_entity_id='customers',
                entityset=es,
                filters=[],
                max_depth=3,
            )
            dfs = DeepFeatureSynthesis(agg_primitives=[Last], **kwargs)

            features = dfs.build_features()

            def find_other_agg_features(features):
                return [f for f in features
                        if (isinstance(f, AggregationFeature) and
                            not isinstance(f, Last)) or
                        len([g for g in f.base_features
                             if isinstance(g, AggregationFeature) and
                             not isinstance(g, Last)]) > 0]

            other_agg_features = find_other_agg_features(features)
            assert len(other_agg_features) == 0

    def test_ignores_entities(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[],
                                       ignore_entities=['log'])

        features = dfs_obj.build_features()
        for f in features:
            deps = f._get_deep_dependencies()
            entities = [d.entity.id for d in deps]
            assert 'log' not in entities

    def test_ignores_variables(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[],
                                       ignore_variables={'log': ['value']})
        features = dfs_obj.build_features()
        for f in features:
            deps = f._get_deep_dependencies()
            identities = [d for d in deps
                          if isinstance(d, IdentityFeature)]
            variables = [d.variable.id for d in identities
                         if d.entity.id == 'log']
            assert 'value' not in variables

    def test_makes_dfeatures(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[],
                                       trans_primitives=[])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'customers.age'))

    def test_makes_trans_feat(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='log',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[],
                                       trans_primitives=[Hour])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'HOUR(datetime)'))

    def test_handles_diff_entity_groupby(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='log',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[],
                                       trans_primitives=[Diff])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'DIFF(value by session_id)'))
        assert (feature_with_name(features, 'DIFF(value by product_id)'))

    def test_handles_time_since_previous_entity_groupby(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='log',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[],
                                       trans_primitives=[TimeSincePrevious])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'time_since_previous_by_session_id'))

    def test_handles_cumsum_entity_groupby(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[],
                                       trans_primitives=[CumMean])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'customers.CUMMEAN(age by region_id)'))

    def test_only_makes_supplied_trans_feat(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='log',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[],
                                       trans_primitives=[Hour])

        features = dfs_obj.build_features()
        other_trans_features = [f for f in features
                                if (isinstance(f, TransformFeature) and
                                    not isinstance(f, Hour)) or
                                len([g for g in f.base_features
                                     if isinstance(g, TransformFeature) and
                                     not isinstance(g, Hour)]) > 0]
        assert len(other_trans_features) == 0

    def test_makes_dfeatures_of_agg_primitives(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[])
        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'customers.LAST(sessions.device_type)'))

    def test_makes_agg_features_of_trans_primitives(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[Hour])

        features = dfs_obj.build_features()
        assert (feature_with_name(features, 'LAST(log.HOUR(datetime))'))

    def test_makes_agg_features_with_where(self, es):
        es.add_interesting_values()

        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Count],
                                       trans_primitives=[])

        features = dfs_obj.build_features()
        assert (feature_with_name(features,
                                  'COUNT(log WHERE priority_level = 0)'))

    def test_abides_by_max_depth_param(self, es):
        for i in [1, 2, 3]:
            dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                           entityset=es,
                                           filters=[],
                                           agg_primitives=[Last],
                                           trans_primitives=[],
                                           max_depth=i)

            features = dfs_obj.build_features()
            for f in features:
                # last feature is identity feature which doesn't count
                assert (f._get_depth() <= i + 1)

    def test_drop_contains(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[],
                                       max_depth=1,
                                       seed_features=[],
                                       drop_contains=[])
        features = dfs_obj.build_features()
        to_drop = features[0]
        partial_name = to_drop.get_name()[:5]
        dfs_drop = DeepFeatureSynthesis(target_entity_id='sessions',
                                        entityset=es,
                                        filters=[],
                                        agg_primitives=[Last],
                                        trans_primitives=[],
                                        max_depth=1,
                                        seed_features=[],
                                        drop_contains=[partial_name])
        features = dfs_drop.build_features()
        assert to_drop.get_name() not in [f.get_name() for f in features]

    def test_drop_exact(self, es):
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[],
                                       max_depth=1,
                                       seed_features=[],
                                       drop_exact=[])
        features = dfs_obj.build_features()
        to_drop = features[0]
        name = to_drop.get_name()
        dfs_drop = DeepFeatureSynthesis(target_entity_id='sessions',
                                        entityset=es,
                                        filters=[],
                                        agg_primitives=[Last],
                                        trans_primitives=[],
                                        max_depth=1,
                                        seed_features=[],
                                        drop_exact=[name])
        features = dfs_drop.build_features()
        assert name not in [f.get_name() for f in features]

    def test_seed_features(self, es):
        seed_feature_sessions = Count(es['log']['value'], es['sessions']) > 2
        seed_feature_log = Hour(es['log']['datetime'])
        session_agg = Last(seed_feature_log, es['sessions'])
        dfs_obj = DeepFeatureSynthesis(target_entity_id='sessions',
                                       entityset=es,
                                       filters=[],
                                       agg_primitives=[Last],
                                       trans_primitives=[],
                                       max_depth=2,
                                       seed_features=[seed_feature_sessions,
                                                      seed_feature_log])
        features = dfs_obj.build_features()
        assert seed_feature_sessions.get_name() in [f.get_name()
                                                    for f in features]
        assert session_agg.get_name() in [f.get_name() for f in features]

    def test_allowed_paths(self, es):
        kwargs = dict(
            target_entity_id='customers',
            entityset=es,
            filters=[],
            agg_primitives=[Last],
            trans_primitives=[],
            max_depth=2,
            seed_features=[]
        )
        dfs_unconstrained = DeepFeatureSynthesis(**kwargs)
        features_unconstrained = dfs_unconstrained.build_features()

        unconstrained_names = [f.get_name() for f in features_unconstrained]
        customers_session_feat = Last(es['sessions']['device_type'],
                                      es['customers'])
        customers_session_log_feat = Last(es['log']['value'], es['customers'])
        assert customers_session_feat.get_name() in unconstrained_names
        assert customers_session_log_feat.get_name() in unconstrained_names

        dfs_constrained = DeepFeatureSynthesis(allowed_paths=[['customers',
                                                               'sessions']],
                                               **kwargs)
        features = dfs_constrained.build_features()
        names = [f.get_name() for f in features]
        assert customers_session_feat.get_name() in names
        assert customers_session_log_feat.get_name() not in names

    def test_max_features(self, es):
        kwargs = dict(
            target_entity_id='customers',
            entityset=es,
            filters=[],
            agg_primitives=[Last],
            trans_primitives=[],
            max_depth=2,
            seed_features=[]
        )
        dfs_unconstrained = DeepFeatureSynthesis(**kwargs)
        features_unconstrained = dfs_unconstrained.build_features()
        dfs_unconstrained_with_arg = DeepFeatureSynthesis(max_features=-1,
                                                          **kwargs)
        features_unconstrained_with_arg = dfs_unconstrained_with_arg.build_features()
        dfs_constrained = DeepFeatureSynthesis(max_features=1, **kwargs)
        features = dfs_constrained.build_features()
        assert len(features_unconstrained) == len(features_unconstrained_with_arg)
        assert len(features) == 1

    def test_where_primitives(self, es):
        es = copy.deepcopy(es)
        es['sessions']['device_type'].interesting_values = [0]
        kwargs = dict(
            target_entity_id='customers',
            entityset=es,
            agg_primitives=[Count, Last],
            max_depth=3,
        )
        dfs_unconstrained = DeepFeatureSynthesis(filters=[], **kwargs)
        dfs_constrained = DeepFeatureSynthesis(where_primitives=[Count], **kwargs)
        features_unconstrained = dfs_unconstrained.build_features()
        features = dfs_constrained.build_features()

        where_feats_unconstrained = [f for f in features_unconstrained
                                     if f.where is not None]
        where_feats = [f for f in features
                       if f.where is not None]
        assert len(where_feats_unconstrained) >= 2

        assert len([f for f in where_feats_unconstrained
                    if isinstance(f, Last)]) > 0
        assert len([f for f in where_feats_unconstrained
                    if isinstance(f, Count)]) > 0

        assert len([f for f in where_feats
                    if isinstance(f, Last)]) == 0
        assert len([f for f in where_feats
                    if isinstance(f, Count)]) > 0

    def test_max_hlevel(self, es):
        kwargs = dict(
            target_entity_id='log',
            entityset=es,
            agg_primitives=[Count, Last],
            trans_primitives=[Hour],
            max_depth=-1,
        )

        dfs_h_n1 = DeepFeatureSynthesis(max_hlevel=-1, **kwargs)
        dfs_h_0 = DeepFeatureSynthesis(max_hlevel=0, **kwargs)
        dfs_h_1 = DeepFeatureSynthesis(max_hlevel=1, **kwargs)
        feats_n1 = dfs_h_n1.build_features()
        feats_n1 = [f.get_name() for f in feats_n1]
        feats_0 = dfs_h_0.build_features()
        feats_0 = [f.get_name() for f in feats_0]
        feats_1 = dfs_h_1.build_features()
        feats_1 = [f.get_name() for f in feats_1]

        customer_log = Last(es['log']['value'], es['customers'])
        session_log = Last(es['log']['value'], es['sessions'])
        log_customer_log = Feature(customer_log, es['log'])
        log_session_log = Feature(session_log, es['log'])
        assert log_customer_log.get_name() in feats_n1
        assert log_session_log.get_name() in feats_n1

        assert log_customer_log.get_name() not in feats_1
        assert log_session_log.get_name() in feats_1

        assert log_customer_log.get_name() not in feats_0
        assert log_session_log.get_name() not in feats_0


class TestDFSMethod(object):
    def test_accepts_cutoff_time_df(self, entities, relationships):
        cutoff_times_df = pd.DataFrame({"instance_id": [1, 2, 3],
                                        "time": [10, 12, 15]})
        feature_matrix, features = dfs(entities=entities,
                                       relationships=relationships,
                                       target_entity="transactions",
                                       cutoff_time=cutoff_times_df)
        assert len(feature_matrix.index) == 3
        assert len(feature_matrix.columns) == len(features)

    def test_accepts_single_cutoff_time(self, entities, relationships):
        feature_matrix, features = dfs(entities=entities,
                                       relationships=relationships,
                                       target_entity="transactions",
                                       cutoff_time=20)
        assert len(feature_matrix.index) == 6
        assert len(feature_matrix.columns) == len(features)

    def test_accepts_no_cutoff_time(self, entities, relationships):
        feature_matrix, features = dfs(entities=entities,
                                       relationships=relationships,
                                       target_entity="transactions",
                                       instance_ids=[1, 2, 3, 5, 6])
        assert len(feature_matrix.index) == 5
        assert len(feature_matrix.columns) == len(features)

    def test_ignores_instance_ids_if_cutoff_df(self, entities, relationships):
        cutoff_times_df = pd.DataFrame({"instance_id": [1, 2, 3],
                                        "time": [10, 12, 15]})
        instance_ids = [1, 2, 3, 4, 5]
        feature_matrix, features = dfs(entities=entities,
                                       relationships=relationships,
                                       target_entity="transactions",
                                       cutoff_time=cutoff_times_df,
                                       instance_ids=instance_ids)
        assert len(feature_matrix.index) == 3
        assert len(feature_matrix.columns) == len(features)

    def test_all_variables(self, entities, relationships):
        cutoff_times_df = pd.DataFrame({"instance_id": [1, 2, 3],
                                        "time": [10, 12, 15]})
        instance_ids = [1, 2, 3, 4, 5]
        feature_matrix, features = dfs(entities=entities,
                                       relationships=relationships,
                                       target_entity="transactions",
                                       cutoff_time=cutoff_times_df,
                                       instance_ids=instance_ids,
                                       agg_primitives=[Max, Mean, Min, Sum],
                                       trans_primitives=[Last],
                                       max_depth=3,
                                       allowed_paths=None,
                                       ignore_entities=None,
                                       ignore_variables=None,
                                       seed_features=None)
        assert len(feature_matrix.index) == 3
        assert len(feature_matrix.columns) == len(features)

    def test_features_only(self, entities, relationships):
        features = dfs(entities=entities,
                       relationships=relationships,
                       target_entity="transactions",
                       features_only=True)
        assert len(features) > 0
