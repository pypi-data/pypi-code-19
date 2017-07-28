__author__ = 'jiyue'
import pandas as pd
from sklearn.datasets import dump_svmlight_file, load_svmlight_file
from sklearn.externals.joblib import Memory

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
