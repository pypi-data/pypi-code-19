from __future__ import print_function
import xgboost as xgb
import numpy as np
import dask.dataframe as dd
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict


# def train_xgb(X_train, y_train, distributed_client=None, **params):
    # # drop out ouliers
    # mask = (y_train > -0.4) & (y_train < 0.419)
    # X_train = X_train[mask]
    # y_train = y_train[mask]

    # print('After removing outliers:')
    # print('Shape train: {}'.format(X_train.shape))
    # if params.get('base_score', None) == 'y_mean':
        # params['base_score'] = np.mean(y_train)
    # if params.get('silent', None) is None:
        # params['silent'] = 1

    # print("\nSetting up data for XGBoost ...")
    # num_boost_rounds = params.pop('num_boost_rounds', 250)
    # if distributed_client:
        # import dask_xgboost as dxgb
        # model = dxgb.train(distributed_client, params, dd.from_array(X_train), dd.from_array(y_train),
                           # num_boost_round=num_boost_rounds)
    # else:
        # dtrain = xgb.DMatrix(X_train, y_train)
        # model = xgb.train(params, dtrain, num_boost_round=num_boost_rounds)

    # return model


# def predict_xgb(model, X_test):
    # dtest = xgb.DMatrix(pd.DataFrame(X_test))
    # print("\nPredicting with XGBoost ...")
    # xgb_pred1 = model.predict(dtest)
    # return xgb_pred1


# def combine_xgb_predictions(xgb_pred1, xgb_pred2, xgb_weight1):
    # return xgb_weight1 * xgb_pred1 + (1 - xgb_weight1) * xgb_pred2


def mask_outliers(X, y, lower_bound=-0.4, upper_bound=0.419):
    mask = (y > -0.4) & (y < 0.419)
    X = X[mask]
    y = y[mask]
    return X, y


def mask__init__(cls, self, **params):
    self.mask = params.pop('mask', False)
    self.mask_lower_bound = params.pop('mask_lower_bound', None)
    self.mask_upper_bound = params.pop('mask_upper_bound', None)
    super(cls, self).__init__(**params)


def mask_fit(cls, self, X, y):
    if self.mask:
        X, y = mask_outliers(X, y)
    super(cls, self).fit(X, y)


class MetaEstimator(BaseEstimator, RegressorMixin):
    params_to_not_pass_through = ['mask',
                                  'mask_lower_bound',
                                  'mask_upper_bound']

    def __init__(self, mask=False, mask_lower_bound=None, mask_upper_bound=None):
        self.mask = mask
        self.mask_lower_bound = mask_lower_bound
        self.mask_upper_bound = mask_upper_bound
        #self.set_params(**params)

    # def set_params(self, **params):
        # super(MetaEstimator, self).set_params(**params)
        # for k, v in params.items():
            # setattr(self, k, v)
        # self._param_keys = params.keys()

    # def get_params(self, deep=False):
        # return {'mask': mask,
                # 'mask_lower_bound':
        # return self.all_params

    # @property
    # def params(self):
        # return {k: getattr(self, k)
                # for k in self._param_keys
                # if k not in self.params_to_not_pass_through}

    # @property
    # def all_params(self):
        # return {k: getattr(self, k)
                # for k in self._param_keys}

    def _get_model(self, X, y):
        pass

    def fit(self, X, y=None):
        if self.mask:
            X, y = mask_outliers(X, y,
                                 lower_bound=self.mask_lower_bound,
                                 upper_bound=self.mask_upper_bound)
        self.model = self._get_model(X, y)
        return self

    def _predict_transform(self, X):
        return X

    def predict(self, X, y=None):
        transformed_X = self._predict_transform(X)
        return self.model.predict(transformed_X)

    def score(self, X, y=None):
        predictions = self.predict(X)
        # Deep mine tries to maximize
        return 1. / mean_absolute_error(y, predictions)


class XGBEstimator(MetaEstimator):
    ignore_params = ['mask', 'mask_lower_bound', 'mask_upper_bound',
                     'distributed_client', 'num_boost_rounds']

    def __init__(self,
                 num_boost_rounds=250,
                 eta=0.3,
                 gamma=0,
                 max_depth=6,
                 min_child_weight=1,
                 max_delta_step=0,
                 subsample=0.8,
                 colsample_bytree=1,
                 colsample_bylevel=1,
                 objective='reg:linear',
                 eval_metric='mae',
                 lambda_=1,
                 alpha=0.4,
                 tree_method='auto',
                 silent=1,
                 base_score='y_mean',
                 distributed_client=None,
                 **meta_params):
        self.num_boost_rounds = num_boost_rounds
        self.eta = eta
        self.gamma=gamma
        self.min_child_weight = min_child_weight
        self.max_delta_step = max_delta_step
        self.max_depth = max_depth
        self.colsample_bylevel=colsample_bylevel
        self.colsample_bytree=colsample_bytree
        self.subsample = subsample
        self.objective = objective
        self.eval_metric = eval_metric
        self.lambda_ = lambda_
        self.alpha = alpha
        self.tree_method = tree_method
        self.silent = silent
        self.base_score = base_score
        self.distributed_client = distributed_client
        super(XGBEstimator, self).__init__(**meta_params)

    @property
    def estimator_params(self):
        params = {k: v for k, v in self.get_params().items()
                  if k not in self.ignore_params}
        params['lambda'] = params.pop('lambda_')
        return params

    def _get_model(self, X, y):
        if self.estimator_params.get('base_score', None) == 'y_mean':
            self.base_score = np.mean(y)

        print('After removing outliers:')
        print("\nTraining XGBoost ...")
        if self.distributed_client:
            import dask_xgboost as dxgb
            model = dxgb.train(self.distributed_client, self.estimator_params, dd.from_array(X), dd.from_array(y),
                               num_boost_round=self.num_boost_rounds)
        else:
            dtrain = xgb.DMatrix(pd.DataFrame(X), pd.DataFrame(y))
            model = xgb.train(self.estimator_params, dtrain, num_boost_round=self.num_boost_rounds)
        return model

    def _predict_transform(self, X):
        print("\nPredicting with XGBoost ...")
        return xgb.DMatrix(pd.DataFrame(X))


class RFWithMask(RandomForestRegressor):
    def __init__(self, **params):
        mask__init__(RFWithMask, self, **params)

    def fit(self, X, y):
        mask_fit(RFWithMask, self, X, y)


class SGDWithMask(SGDRegressor):
    def __init__(self, **params):
        mask__init__(SGDWithMask, self, **params)

    def fit(self, X, y):
        mask_fit(SGDWithMask, self, X, y)


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


class EnsembleEstimator(MetaEstimator):
    def __init__(self, estimator_objects, client=None, ensemble_baseline_weight=0.05,
                 ensemble_baseline_pred=0.0155, **params):
        super(EnsembleEstimator, self).__init__(**params)

        self.client = client
        self.ensemble_baseline_weight = ensemble_baseline_weight
        self.ensemble_baseline_pred = ensemble_baseline_pred
        self._estimator_objects = estimator_objects
        self._estimators = {}
        self._weights = None
        self.set_params(**params)

    def get_params(self, deep=False):
        params = {'ensemble_baseline_weight': self.ensemble_baseline_weight}
        if len(self._estimators) == 0:
            self.set_params()
        for n, est in self._estimators.items():
            est_params = est.get_params(deep=deep)
            for k, v in est_params.items():
                params['ensemble_{}_{}'.format(n, k)] = v
        return params

    def set_params(self, **params):
        estimator_params = defaultdict(dict)
        weights = {}
        for k, v in params.items():
            k = k.replace('ensemble_', '')
            est = k.split('_')[0]
            if est == 'weight':
                weights[k.replace('weight_', '')] = v
            elif est in self._estimator_objects:
                param_key = k.replace(est + '_', '')
                estimator_params[est][param_key] = v
            else:
                setattr(self, k, v)
        for est, o in self._estimator_objects.items():
            est_params = estimator_params.get(est, {})
            if isinstance(o, XGBEstimator):
                est_params['distributed_client'] = self.client
            self._estimators[est] = o(**est_params)
        if self._weights is None or len(weights):
            self.set_weights(weights)

    def _get_model(self, X, y):
        for name, estimator in self._estimators.items():
            self._estimators[name].fit(X, y)

    def set_weights(self, weights):
        baseline_weight = self.ensemble_baseline_weight
        if len(weights) == 0:
            weights = {est: 1 for est in self._estimators}
        elif len(weights) < len(self._estimators):
            for est in self._estimators:
                if est not in weights:
                    weights[est] = 0
        assert len(weights) == len(self._estimators)
        weights['baseline_weight'] = baseline_weight
        simplex_weights = softmax(np.array(weights.values()))
        self._weights = {k: simplex_weights[i] for i, k in enumerate(weights.keys())}

    def predict(self, X, y=None):
        combined = []
        for name, estimator in self._estimators.items():
            pred = self._weights[name] * estimator.predict(X)
            combined.append(pred)
        combined.append(self._weights['baseline_weight'] * self.ensemble_baseline_pred)
        return sum(combined)
