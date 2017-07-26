from lib.manipulation import _slice_list
import numpy as np


def test_easy_string():
    a = np.array([[1,2,3,4,5,6,7,8,9,0]])
    sliced,_ = _slice_list(a,"0")
    expected = [1]
    assert sliced == expected


def test_moderate_string():
    a = np.array([[1,2,3,4,5,6,7,8,9,0]])
    sliced,_ = _slice_list(a,"0,4,7")
    expected = [[1,5,8]]
    assert np.array_equal(expected, sliced)


def test_harder_string():
    a = np.array([[1,2,3,4,5,6,7,8,9,0]])
    sliced,_ = _slice_list(a,"0,4:6,9")
    expected = [[1,5,6,7,0]]
    assert  np.array_equal(expected, sliced)


def test_with_only_colon():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, ":")
    expected = [[1,2,3,4, 5, 6, 7,8,9, 0]]
    assert np.array_equal(expected, sliced)


def test_with_minus_one():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "0,-1")
    expected = [[1, 0]]
    assert np.array_equal(expected, sliced)


def test_with_minus_two():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "0,-2")
    expected = [[1, 9]]
    assert np.array_equal(expected, sliced)


def test_with_colon_from_minus_4_to_minus_two():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "-4:-2")
    expected = [[7,8,9]]
    assert np.array_equal(expected, sliced)


def test_with_colon_from_minus_4_to_minus_two_with_more_dimensions():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0],[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "-4:-2")
    expected = [[7, 8, 9],[7, 8, 9]]
    assert np.array_equal(expected, sliced)


def test_with_colon_from_four_to_minus_two_with_more_dimensions():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "4:-2")
    expected = [[5, 6, 7, 8, 9], [5, 6, 7, 8, 9]]
    assert np.array_equal(expected, sliced)


def test_with_colon_and_negative_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, ":-2")
    expected = [[1,2,3,4,5,6,7,8,9]]
    assert np.array_equal(expected, sliced)


def test_with_colon_and_positive_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, ":2")
    expected = [[1, 2, 3]]
    assert np.array_equal(expected, sliced)


def test_with_colon_at_the_end_and_negative_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "-2:")
    expected = [[9,0]]
    assert np.array_equal(expected, sliced)


def test_with_colon_at_the_end_and_positive_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "2:")
    expected = [[3, 4, 5, 6, 7, 8, 9, 0]]
    assert np.array_equal(expected, sliced)


def test_remove_with_colon_at_the_end_and_positive_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "2:", keep=False)
    expected = [[1, 2]]
    assert np.array_equal(expected, sliced)

def test_remove_with_colon_at_the_end_and_negative_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "-2:", keep=False)
    expected = [[1, 2, 3, 4, 5, 6, 7, 8]]
    assert np.array_equal(expected, sliced)

def test_remove_with_colon_and_positive_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, ":2", keep=False)
    expected = [[4, 5, 6, 7, 8, 9, 0]]
    assert np.array_equal(expected, sliced)

def test_remove_easy_string():
    a = np.array([[1,2,3,4,5,6,7,8,9,0]])
    sliced,_ = _slice_list(a,"0",keep=False)
    expected = [[2,3,4,5,6,7,8,9,0]]
    assert np.array_equal(sliced,expected)


def test_remove_moderate_string():
    a = np.array([[1,2,3,4,5,6,7,8,9,0]])
    sliced,_ = _slice_list(a,"0,4,7",keep=False)
    expected = [[2,3,4,6,7,9,0]]
    assert np.array_equal(expected, sliced)


def test_remove_harder_string():
    a = np.array([[1,2,3,4,5,6,7,8,9,0]])
    sliced,_ = _slice_list(a,"0,4:6,9",keep=False)
    expected = [[2,3,4,8,9]]
    assert  np.array_equal(expected, sliced)


def test_remove_with_only_colon():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, ":",keep=False)
    expected = [[]]
    assert np.array_equal(expected, sliced)


def test_remove_with_minus_one():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "0,-1",keep=False)
    expected = [[2, 3, 4, 5, 6, 7, 8, 9]]
    assert np.array_equal(expected, sliced)


def test_remove_with_minus_two():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "0,-2",keep=False)
    expected = [[ 2, 3, 4, 5, 6, 7, 8, 0]]
    assert np.array_equal(expected, sliced)


def test_remove_with_colon_from_minus_4_to_minus_two():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, "-4:-2",keep=False)
    expected = [[1, 2, 3, 4, 5, 6, 0]]
    print("slices, expected: ",sliced,expected)
    assert np.array_equal(expected, sliced)



def test_remove_with_colon_and_negative_number():
    a = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]])
    sliced,_ = _slice_list(a, ":-2", keep=False)
    expected = [[0]]
    assert np.array_equal(expected, sliced)