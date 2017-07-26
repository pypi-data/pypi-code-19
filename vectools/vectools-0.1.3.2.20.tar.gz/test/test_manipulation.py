import numpy as np
from lib.manipulation import _append_row, _append_column


def test_append_row():
    matrix = np.array([[1, 2], [3, 4]])
    value = 0
    rows = None
    position = -1
    target_matrix = np.array([[1, 2], [3, 4], [0, 0]])
    matrix = _append_row(matrix, rows, position, value)
    assert np.array_equal(target_matrix, matrix)
    assert rows is None
    value = 'a'
    rows = ["a", "b", "c"]
    position = 0
    matrix = _append_row(matrix, rows, position, value)
    target_matrix = np.array([["a", "a"], ["1", "2"], ["3", "4"], ["0", "0"]])
    assert np.array_equal(target_matrix, matrix)
    assert rows == ["r0", "a", "b", "c"]


def test_append_column():
    matrix = np.array([[1, 2], [3, 4]])
    value = 0
    cols = None
    position = -1
    target_matrix = np.array([[1, 2, 0], [3, 4, 0]])
    matrix = _append_column(matrix, cols, position, value)
    assert np.array_equal(target_matrix,matrix)
    assert cols is None
    value = 'a'
    cols = ["a", "b", "c"]
    position = 0
    matrix = _append_column(matrix, cols, position, value)
    target_matrix = np.array([["a", "1", "2", "0"], ["a", "3", "4", "0"]])
    assert np.array_equal(target_matrix, matrix)
    assert cols == ["c0", "a", "b", "c"]
