import pandas as pd
import numpy as np
from distributed import Client
from sklearn.linear_model import LinearRegression, SGDRegressor
# from lgb import train_lgb, predict_lgb
from estimators import RFEstimator, SGDEstimator, XGBEstimator
import gc
from sklearn.preprocessing import Imputer, StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold


XGB_WEIGHT = 0.6840
BASELINE_WEIGHT = 0.0056
OLS_WEIGHT = 0#0.0550
XGB1_WEIGHT = 0.8083  # Weight of first in combination of two XGB models
BASELINE_PRED = 0.0115   # Baseline based on mean of training data, per Oleg

LGB_PARAMS = {
    'max_bin': 10,
    # shrinkage_rate
    'learning_rate': 0.0021,
    'boosting_type': 'gbdt',
    'objective': 'regression',
    # or 'mae'
    'metric': 'l1',
    # feature_fraction -- OK, back to .5, but maybe later increase this
    'sub_feature': 0.5,
    # sub_row
    'bagging_fraction': 0.85,
    'bagging_freq': 40,
    # num_leaf
    'num_leaves': 512,
    # min_data_in_leaf
    'min_data': 500,
    # min_sum_hessian_in_leaf
    'min_hessian': 0.05,
    'verbose': 0,
    'num_boost_rounds': 430
}


XGB_PARAMS_1 = {
    'num_boost_rounds': 250,
    'eta': 0.037,
    'max_depth': 5,
    'subsample': 0.80,
    'objective': 'reg:linear',
    'eval_metric': 'mae',
    'lambda': 0.8,
    'alpha': 0.4,
    'base_score': 'y_mean',
    'silent': 1
    'mask': True,
    'mask_lower_bound': -0.4,
    'mask_upper_bound': 0.419
}


XGB_PARAMS_2 = {
    'num_boost_rounds': 150,
    'eta': 0.033,
    'max_depth': 6,
    'subsample': 0.80,
    'objective': 'reg:linear',
    'eval_metric': 'mae',
    'base_score': 'y_mean',
    'silent': 1
    'mask': True,
    'mask_lower_bound': -0.4,
    'mask_upper_bound': 0.419
}


SGD_PARAMS = {
    'loss': 'huber',
    'penalty': 'elasticnet',
    'alpha': 0.0001,
    'l1_ratio': 0.15,
    'fit_intercept': True,
    'n_iter': 10,
    'epsilon': 0.1,
    'learning_rate': 'invscaling',
    'eta0': 0.01,
    'power_t': 0.25,
    'verbose': 0,
}


def train_and_predict(X_train, y_train, X_test, client=None):
    fitted_linreg = train_linreg(X_train, y_train)
    linreg_pred = predict_linreg(fitted_linreg, X_test)

    fitted_sgd = train_sgd(X_train, y_train, **SGD_PARAMS)
    sgd_pred = predict_sgd(fitted_sgd, X_test)

    # fitted_lgb = train_lgb(X_train, y_train, **LGB_PARAMS)
    # lgb_pred = predict_lgb(fitted_lgb, X_test)
    # del fitted_lgb
    # gc.collect()

    fitted_xgb1 = train_xgb(X_train, y_train, distributed_client=client, **XGB_PARAMS_1)
    xgb1_pred = predict_xgb(fitted_xgb1, X_test)
    del fitted_xgb1
    gc.collect()
    fitted_xgb2 = train_xgb(X_train, y_train, distributed_client=client, **XGB_PARAMS_2)
    xgb2_pred = predict_xgb(fitted_xgb2, X_test)
    del fitted_xgb2

    del X_train, y_train, X_test
    gc.collect()

    xgb_pred = combine_xgb_predictions(xgb1_pred, xgb2_pred, XGB1_WEIGHT)
    predictions = combine_predictions(xgb_pred, sgd_pred, linreg_pred, BASELINE_PRED)
    return predictions


def combine_predictions(xgb_pred, sgd_pred, linreg_pred, BASELINE_PRED):
    sgd_weight = (1 - XGB_WEIGHT - BASELINE_WEIGHT) / (1 - OLS_WEIGHT)
    xgb_weight0 = XGB_WEIGHT / (1 - OLS_WEIGHT)
    baseline_weight0 = BASELINE_WEIGHT / (1 - OLS_WEIGHT)
    pred0 = xgb_weight0 * xgb_pred + baseline_weight0 * BASELINE_WEIGHT + sgd_weight * sgd_pred

    pred = OLS_WEIGHT * linreg_pred + (1 - OLS_WEIGHT) * pred0
    return pred


def train_linreg(X_train, y_train):
    print "Training linear regression"
    reg = LinearRegression(n_jobs=-1)
    reg.fit(X_train, y_train)
    return reg


def train_sgd(X_train, y_train, **sgd_params):
    print "Training SGD"
    reg = SGDRegressor(**sgd_params)
    reg.fit(X_train, y_train)
    return reg


def predict_linreg(reg, X_test):
    return reg.predict(X_test)


def predict_sgd(sgd, X_test):
    return sgd.predict(X_test)


def estimate_cross_val(fm_file='high_variance_fm_full.p', folds=3, client=None, sample=None):
    preprocessor = Pipeline([("imputer", Imputer(missing_values='NaN',
                                                 strategy="most_frequent",
                                                 axis=0)),
                             ("scaler", StandardScaler())])
    feature_matrix = pd.read_pickle(fm_file)
    if sample is not None:
        feature_matrix = feature_matrix.sample(1000)
    used_features = [c for c in feature_matrix.columns
                     if c not in ['logerror', 'parcelid']]
    X = feature_matrix[used_features].values
    X = preprocessor.fit_transform(X)
    y = feature_matrix['logerror'].values.astype(np.float32)

    splitter = KFold(folds)
    folds = splitter.split(X, y)
    predictions = []
    actual_scores = []
    args = []
    for i, fold in enumerate(folds):
        print "Fold %s" % i
        train_i, test_i = fold
        X_train = X[train_i]
        X_test = X[test_i]
        y_train = y[train_i]
        y_test = y[test_i]
        actual_scores.append(y_test)
        args.append((X_train, y_train, X_test))

        pred = train_and_predict(X_train, y_train, X_test, client=client)
        predictions.append(pred)

    predictions = evaluate(predictions, actual_scores)
    predictions.to_pickle('combined_model_predictions.p')
    return predictions


def evaluate(predictions, actual_scores):
    metrics = [('Mean Absolute Error', mean_absolute_error), ('Mean Square Error', mean_squared_error), ('R2', r2_score)]
    scores = []

    for name, metric in metrics:
        metric_scores = [metric(actual, pred)
                         for actual, pred in zip(actual_scores, predictions)]
        mean = np.mean(metric_scores)
        std = np.std(metric_scores)
        print "{}: {} +/- {}".format(name, mean, std)
        scores.append((name, mean, std))
    scores = pd.DataFrame(scores, columns=['Metric', 'Mean', 'Std'])
    return scores


if __name__ == '__main__':
    host = '34.205.85.166:8786'
    client = Client(host)
    estimate_cross_val(fm_file='high_variance_fm_25k.p', client=client)#, sample=1000)
