from lib.analysis import  _pearson_calc, _column_wise_calculation
import numpy as np


def test_nose():
    assert 'b' == 'b'


def test_pearson_calc():
    dok = dict()
    group1 = "lincRNA"
    group2 = "protein_coding"
    key1 = "ENSG123456"
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    key2 = "ENSG234567"
    y = [2, 4, 6, 8, 10, 12, 14, 16]
    dok[group1] = {}
    dok[group2] = {}
    dok[group1][key1] = x
    dok[group2][key2] = y
    pct = 0.9
    pv = 0.05
    pear = 1.0
    p_value = 0.0
    results = ["{}_{}".format(group1, group2), "{}_{}".format(key1, key2), pear, p_value]
    for index, value in enumerate(dok[group1][key1]):
        results.extend((value, dok[group2][key2][index]))
    assert _pearson_calc(dok, group1, group2, key1, key2, x, y, pct, pv) == results


def test_column_wise_calculation():

    diag = (1, 2, 3, 4, 5, 6)
    matrix = np.diag(diag)
    assert _column_wise_calculation(matrix, np.max) == [[1, 2, 3, 4, 5, 6]]
    assert _column_wise_calculation(matrix, np.min) == [[0, 0, 0, 0, 0, 0]]
    assert _column_wise_calculation(matrix, np.median) == [[0, 0, 0, 0, 0, 0]]
    assert _column_wise_calculation(matrix, np.mean) == [[1 / 6., 2 / 6., 3 / 6., 4 / 6., 5 / 6., 1]]