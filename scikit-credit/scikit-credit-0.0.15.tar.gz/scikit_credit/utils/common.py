__author__ = 'jiyue'
import pandas as pd
import math
from sklearn.datasets import dump_svmlight_file, load_svmlight_file
from sklearn.externals.joblib import Memory
import numpy as np

mem = Memory("~/.svmmem")


def compute_missing_pct(dataframe, dtype):
    dataframe.select_dtypes(include=[dtype]).describe().T \
        .assign(missing_pct=dataframe.apply(lambda x: (len(x) - x.count()) / float(len(x))))


def dump_to_svm_format_file(data_frame, label='label', file_name='svm-output.libsvm'):
    dummy = pd.get_dummies(data_frame)
    y = data_frame[label]
    mat = dummy.as_matrix()
    dump_svmlight_file(mat, y, file_name)


def load_svm_format_file(path):
    data = load_svmlight_file(path)
    return data[0], data[1]


def cal_sigmod(x):
    one = 1.0
    return one / (one + math.exp(-x))


def cal_predict_prob(weights):
    inner = 0.0
    for i in weights:
        inner += i
    return cal_sigmod(inner)


def cal_aplus_score(pred):
    BASE_SCORE = 600
    init_score = BASE_SCORE - 20 / math.log(2) * math.log(60) + 20 / math.log(2) * math.log(
        (1 - pred) / (pred + 0.000001))
    return int(init_score)


def cal_weight(encoding_file_path, header=False):
    res = dict()
    with open(encoding_file_path, 'r') as f:
        list_all_data = f.readlines()
        for idx, item in enumerate(list_all_data):
            if not header and idx == 0:
                continue
            sign = item.split('\t')[0]
            weight = item.split('\t')[1]

            feature_name = sign.split('$')[0]
            feature_binning_range = sign.split('$')[1]

            if feature_name not in res:
                res[feature_name] = dict()
                res[feature_name]['bins'] = list()
                res[feature_name]['weight'] = list()

            res[feature_name]['bins'].append(
                (int(feature_binning_range.split('~')[0]), int(feature_binning_range.split('~')[1])))
            res[feature_name]['weight'].append(weight)
    return res


def cal_user_query_score(encoding_file_path, output_file_handler, sample, estimator=None):
    weight_list = list()
    mapping_res = cal_weight(encoding_file_path)
    for feature_name, feature_item in mapping_res.iteritems():
        for fea_key, fea_value in sample.iteritems():
            if feature_name == fea_key:
                bins_range = mapping_res[feature_name]['bins']
                for index, item_range in enumerate(bins_range):
                    if fea_value >= item_range[0] and fea_value < item_range[1]:
                        weight_list.append(float(mapping_res[feature_name]['weight'][index]))

    if not estimator:
        prob = cal_predict_prob(weight_list)
    else:
        columns = list()
        data = list()
        for col_name, col_value in sample.iteritems():
            columns.append(col_name)
            data.append(col_value)

        prob = estimator.do_predict(np.array(data))[1]
    score = cal_aplus_score(prob)

    for k, v in sample.iteritems():
        print str(k) + ':' + str(v) + ' '
        output_file_handler.write(str(v) + ' ')
    output_file_handler.write(str(round(prob, 3)) + ' ')
    output_file_handler.write(str(score) + '\n')
    print score
    return score
