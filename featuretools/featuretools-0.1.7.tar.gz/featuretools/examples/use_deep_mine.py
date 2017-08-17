import dm_setup
from deep_mine import DeepMine, set_hyperparams_dm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Imputer, StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import FunctionTransformer
from estimators import EnsembleEstimator, SGDWithMask, XGBEstimator, RFWithMask
from distributed import Client
import copy
import pandas as pd
import numpy as np
import gc

ESTIMATOR_PARAMS = {
    'sgd': {
        'object': SGDWithMask,
        'params': {
            'loss': ['cat', ['huber']],
            'penalty': ['cat', ['elasticnet']],
            'alpha': ['float', [1e-5, 1e-1]],
            'l1_ratio': ['float', [0, 1]],
            'fit_intercept': ['cat', [True]],
            'n_iter': ['int', [3, 20]],
            'epsilon': ['float', [1e-5, 0.1]],
            'learning_rate': ['cat', ['optimal', 'invscaling']],
            'eta0': ['float', [1e-3, 0.1]],
            'power_t': ['float', [0.1, 0.5]],
            'verbose': ['int', [0]],
            'mask': ['cat', [True, False]],
        },
    },
    'rf': {
        'object': RFWithMask,
        'params': {
            'n_estimators': ['int', [10, 200]],
            'mask': ['cat', [True, False]],
        },
    },
    'xgb': {
        'object': XGBEstimator,
        'params': {
            'num_boost_rounds': ['int', [50, 400]],
            'eta': ['float', [0.001, 0.6]],
            'gamma': ['float', [0, 1e9]],
            'max_depth': ['int', [1, 10]],
            'subsample': ['float', [0.1, 1]],
            'min_child_weight': ['float', [0, 1e9]],
            # 'min_child_weight': ['float', [1]],
            'max_delta_step': ['float', [0, 10]],
            # 'max_delta_step': ['float', [0]],
            'colsample_bylevel': ['float', [0, 1]],
            'colsample_bytree': ['float', [0, 1]],
            'objective': ['cat', ['reg:linear', 'reg:gamma', 'reg:tweedie']],
            'eval_metric': ['cat', ['mae']],
            'lambda_': ['float', [0, 1e9]],
            # 'lambda_': ['float', [1]],
            'alpha': ['float', [0, 1e9]],
            # 'alpha': ['float', [0]],
            'base_score': ['cat', ['y_mean']],
            'silent': ['int', [1]],
            'mask': ['cat', [True, False]],
            'mask_lower_bound': ['float', [-0.4]],
            'mask_upper_bound': ['float', [0.419]]
        },
    },

}
ESTIMATOR_PARAMS['xgb1'] = ESTIMATOR_PARAMS.pop('xgb')
ESTIMATOR_PARAMS['xgb2'] = copy.copy(ESTIMATOR_PARAMS['xgb1'])
ESTIMATOR_PARAMS = {
    'sgd': {
        'object': SGDWithMask,
        'params': {
            'loss': ['cat', ['huber']],
            'penalty': ['cat', ['elasticnet']],
            'alpha': ['float', [1e-5, 1e-3]],
            'l1_ratio': ['float', [0.1, 0.5]],
            'fit_intercept': ['cat', [True]],
            'n_iter': ['int', [5, 15]],
            # 'epsilon': ['float', [1e-5, 0.1]],
            'learning_rate': ['cat', ['optimal']],
            'eta0': ['float', [0.01]],
            'power_t': ['float', [0.25]],
            'verbose': ['int', [0]],
            'mask': ['cat', [False]],
        },
    },
    'rf': {
        'object': RFWithMask,
        'params': {
            'n_estimators': ['int', [10, 200]],
            'mask': ['cat', [False]],
        },
    },
    'xgb1': {
        'object': XGBEstimator,
        'params': {
            'num_boost_rounds': ['int', [200, 300]],
            'eta': ['float', [0.03, .04]],
            'max_depth': ['int', [3, 6]],
            'subsample': ['float', [0.7, 0.9]],
            'objective': ['cat', ['reg:linear']],
            'eval_metric': ['cat', ['mae']],
            'lambda_': ['float', [0.6, 0.9]],
            'alpha': ['float', [0.3, 0.5]],
            'base_score': ['cat', ['y_mean']],
            'silent': ['int', [1]],
            'mask': ['cat', [True, False]],
        },
    },
    'xgb2': {
        'object': XGBEstimator,
        'params': {
            'num_boost_rounds': ['int', [100, 200]],
            'eta': ['float', [0.03, .04]],
            'max_depth': ['int', [5, 8]],
            'subsample': ['float', [0.7, 0.9]],
            'objective': ['cat', ['reg:linear']],
            'eval_metric': ['cat', ['mae']],
            'base_score': ['cat', ['y_mean']],
            'silent': ['int', [1]],
            'mask': ['cat', [True, False]],
        },
    },
}


def create_hm_ranges(estimator_params, n_features):

    hyperparam_ranges = {
        'imputer_strategy': ['cat', ['mean', 'median', 'most_frequent']],
        'scaler_scale_type': ['cat', ['standard', 'robust']],
        # 'pca_n_components': ['int', [10, n_features]],
        'ensemble_baseline_weight': ['float', [0, .05]],
        'ensemble_weight_sgd': ['float', [3, 9]],
        'ensemble_weight_rf': ['float', [3, 9]],
        'ensemble_weight_xgb1': ['float', [4, 5]],
        'ensemble_weight_xgb2': ['float', [0, 3]],
    }

    for est, est_info in estimator_params.items():
        params = est_info['params']
        for k, v in params.items():
            pkey = 'ensemble_{}_{}'.format(est, k)
            hyperparam_ranges[pkey] = v
        # weight = ['float', [0, 9]]
        # weight_key = 'ensemble_weight_{}'.format(est)
        # hyperparam_ranges[weight_key] = weight

    return hyperparam_ranges


def maybe_use_pca(X, n_components=0):
    if n_components < 10 or (X.shape[1] - n_components) < 10:
        return X
    else:
        pca = PCA(n_components=n_components)
        return pca.fit_transform(X)


def choose_scaler(X, scale_type, with_centering=False):
    if scale_type == 'standard':
        scaler = StandardScaler()
    else:
        scaler = RobustScaler(with_centering=with_centering)
    return scaler.fit_transform(X)


def set_pipeline(hyperparam_dict, client):
    # pca = FunctionTransformer(func=maybe_use_pca, validate=False)
    scaler = FunctionTransformer(func=choose_scaler, validate=False)
    estimator_objects = {k: v['object'] for k, v in ESTIMATOR_PARAMS.items()}

    ensemble = EnsembleEstimator(estimator_objects, client=client)
    pipeline = Pipeline([
        ("imputer", Imputer(missing_values='NaN', axis=0)),
        ("scaler", scaler),
        # ('pca', pca),
        ('ensemble', ensemble)
    ])

    steps_params_list = []
    for k in hyperparam_dict:
        for est in pipeline.named_steps:
            if k.startswith(est):
                new_k = k.replace(est + '_', '')
                steps_params_list.append((est, new_k, k))

    pipeline = set_hyperparams_dm(pipeline, hyperparam_dict, steps_params_list)
    return pipeline


class DataObject(object):
    def __init__(self, fm_path):
        feature_matrix = pd.read_pickle(fm_path)
        used_features = [c for c in feature_matrix.columns
                         if c not in ['logerror', 'parcelid']]
        X = feature_matrix[used_features].values
        y = feature_matrix['logerror'].values.astype(np.float32)
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(X, y, test_size=0.33)
        del feature_matrix
        del X
        del y
        gc.collect()


def run_deepmine(fm_path='high_variance_fm_full.p'):
    data = DataObject(fm_path)
    n_features = data.X_train.shape[1]
    hyperparam_ranges = create_hm_ranges(ESTIMATOR_PARAMS, n_features)
    client = Client('34.205.252.210:8786')
    final_pipeline, performances = DeepMine(data=data,
                                            set_pipeline=lambda hyperparam_dict: set_pipeline(hyperparam_dict, client),
                                            hyperparam_ranges=hyperparam_ranges,
                                            store_performances=True,
                                            num_total_iter=50,
                                            parallelized=0)
    return final_pipeline, performances
