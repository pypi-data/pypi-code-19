from datetime import datetime

import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal


def test_delete_series_without_slices(a_series, series, data):
    assert series.find({'_id': a_series.id}, {'_id': 1}).limit(1).count() == 1
    assert data.find({}, {'_id': 1}).count() == 0
    assert a_series.id is not None
    a_series.delete()
    assert series.find({'_id': a_series.id}, {'_id': 1}).limit(1).count() == 0
    assert data.find({}, {'_id': 1}).count() == 0
    assert a_series.id is None
    

def test_add_slice(a_series, series, data):
    start = datetime(2017, 3, 4)
    slice = a_series.add_slice(start)
    assert slice.start == start
    assert data.find({}, {'_id': 1}).count() == 1
    id = data.find({}, {'_id': 1})[0]['_id']
    assert slice.id == id
    assert slice.collection == data
    assert slice.series == a_series
    assert slice.num_of_samples == 0
    assert len(a_series.slices) == 1
    assert slice.series == a_series
    assert slice.is_sparse == False
    

def test_add_sparse_slice(a_series, series, data):
    start = datetime(2017, 3, 4)
    slice = a_series.add_slice(start, is_sparse=True)
    assert slice.start == start
    assert data.find({}, {'_id': 1}).count() == 1
    id = data.find({}, {'_id': 1})[0]['_id']
    assert slice.id == id
    assert slice.collection == data
    assert slice.series == a_series
    assert slice.num_of_samples == 0
    assert len(a_series.slices) == 1
    assert slice.series == a_series
    assert slice.is_sparse == True


def test_delete_slice(a_series, a_slice, data):
    a_slice.delete()
    assert a_slice.id is None
    assert data.find({}, {'_id': 1}).count() == 0
    assert len(a_series.slices) == 0
    
    
def test_delete_sparse_slice(a_series, a_sparse_slice, data):
    a_sparse_slice.delete()
    assert a_sparse_slice.id is None
    assert data.find({}, {'_id': 1}).count() == 0
    assert len(a_series.slices) == 0
    
    
def test_delete_series_with_slices(a_series, a_slice, data):
    a_series.delete()
    assert len(a_series.slices) == 0
    assert a_series.id is None
    assert a_slice.id is None
    assert data.find({}, {'_id': 1}).count() == 0
    
    
def test_add_one_data_point_to_slice(a_slice, data):
    input = [['abc', 1, 2, 3]]
    a_slice.add(input)
    assert a_slice.num_of_samples == 1
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == input
    
    
def test_add_one_data_point_to_slice_with_input_as_dict(a_slice, data):
    input = [{'col1': 'abc', 'col2': 1}]
    a_slice.add(input)
    assert a_slice.num_of_samples == 1
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == [['abc', 1]]
    
    
def test_add_one_data_point_to_sparse_slice(a_sparse_slice, data):
    input = {datetime(2017, 3, 8): ['abc', 1, 2, 3]}
    a_sparse_slice.add(input)
    assert a_sparse_slice.num_of_samples == 1
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == [{'timestamp': datetime(2017, 3, 8), 'data': ['abc', 1, 2, 3]}]
    
    
def test_add_one_data_point_to_sparse_slice_with_input_as_dict(a_sparse_slice, data):
    input = {np.datetime64(datetime(2017, 3, 8)): {'col1': 'abc', 'col2': 1}}
    a_sparse_slice.add(input)
    assert a_sparse_slice.num_of_samples == 1
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == [{'timestamp': datetime(2017, 3, 8), 'data': ['abc', 1]}]
    

def test_add_two_data_points_to_slice(a_slice, data):
    input = [['abc', 1, 2, 3], ['bcd', 2, 3, 4]]
    a_slice.add(input)
    assert a_slice.num_of_samples == 2
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == input
    

def test_add_two_data_points_to_sparse_slice(a_sparse_slice, data):
    input = {datetime(2017, 3, 8): ['abc', 1, 2, 3], 
             datetime(2017, 3, 9): ['bcd', 2, 3, 4]}
    a_sparse_slice.add(input)
    assert a_sparse_slice.num_of_samples == 2
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0]
    assert stored_data['data'] == [{'timestamp': datetime(2017, 3, 9), 'data': ['bcd', 2, 3, 4]}, 
                                   {'timestamp': datetime(2017, 3, 8), 'data': ['abc', 1, 2, 3]}]
    
    
def test_add_data_into_slices_which_already_has_data(a_slice, data):
    input = [['abc', 1, 2, 3]]
    a_slice.add(input)
    a_slice.add(input)
    assert a_slice.num_of_samples == 2
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0] 
    assert stored_data['data'] == [input[0], input[0]]


def test_add_data_into_sparse_slices_which_already_has_data(a_sparse_slice, data):
    a_sparse_slice.add({datetime(2017, 3, 8): ['abc', 1, 2, 3]})
    a_sparse_slice.add({datetime(2017, 3, 9): ['bcd', 2, 3, 4]})
    assert a_sparse_slice.num_of_samples == 2
    stored_data = data.find({})
    assert stored_data.count() == 1
    stored_data = stored_data[0]
    assert stored_data['data'] == [{'timestamp': datetime(2017, 3, 8), 'data': ['abc', 1, 2, 3]},
                                   {'timestamp': datetime(2017, 3, 9), 'data': ['bcd', 2, 3, 4]}]

    
def test_get_data_from_slice(a_slice, data):
    output = a_slice.get()
    assert output == []
    a_slice.add([['abc', 1, 2, 3]])
    output = a_slice.get()
    assert [[np.datetime64(datetime(2017, 3, 4)), 'abc', 1, 2, 3]] == output


def test_get_data_from_sparse_slice(a_sparse_slice, data):
    output = a_sparse_slice.get()
    assert output == []
    a_sparse_slice.add({datetime(2017, 3, 8): ['abc', 1, 2, 3]})
    output = a_sparse_slice.get()
    assert [[np.datetime64(datetime(2017, 3, 8)), 'abc', 1, 2, 3]] == output
    

def test_slice_end_property(a_series, a_slice):
    a_series.frequency = '1d'
    a_slice.start = datetime(2017, 3, 4)
    assert a_slice.start == a_slice.end
    a_slice.add([1])
    assert a_slice.end == datetime(2017, 3, 5)
    assert type(a_slice.end) == datetime


def test_sparse_slice_end_property(a_sparse_slice, data):
    a_sparse_slice.start = datetime(2017, 3, 4)
    assert a_sparse_slice.start == a_sparse_slice.end
    a_sparse_slice.add({datetime(2017, 3, 8): ['abc', 1, 2, 3]})
    assert a_sparse_slice.end == datetime(2017, 3, 8)
    assert type(a_sparse_slice.end) == datetime
    a_sparse_slice.add({datetime(2017, 3, 9): ['abc', 1, 2, 3],
                        datetime(2017, 3, 10): ['abc', 1, 2, 3]})
    assert a_sparse_slice.end == datetime(2017, 3, 10)
    assert type(a_sparse_slice.end) == datetime
    

def test_get_data_from_series(a_series, a_slice):
    a_series.frequency = '1d'
    a_slice.start = datetime(2017, 3, 4)
    a_slice.add([[1, 2], [3, 4]])
    results = a_series.get()
    expected = pd.DataFrame({'col1': [1., 3.], 'col2': [2., 4.], 'time': [datetime(2017, 3, 4), datetime(2017, 3, 5)]})
    expected.set_index('time', inplace=True)
    assert_frame_equal(expected, results, check_dtype=False)
    

def test_get_data_from_slice_with_filters(a_series, a_slice, data):
    a_series.frequency = '1d'
    a_slice.start = datetime(2017, 3, 4)
    a_slice.add([[1], [2], [3], [4], [5]])
    output = a_slice.get()
    assert output == [[np.datetime64(datetime(2017, 3, 4)), 1], \
                      [np.datetime64(datetime(2017, 3, 5)), 2], \
                      [np.datetime64(datetime(2017, 3, 6)), 3], \
                      [np.datetime64(datetime(2017, 3, 7)), 4], \
                      [np.datetime64(datetime(2017, 3, 8)), 5]]
    output = a_slice.get(data_from=datetime(2017, 3, 4), data_to=datetime(2017, 3, 4))
    assert output == [[np.datetime64(datetime(2017, 3, 4)), 1]]
    output = a_slice.get(data_from=datetime(2017, 3, 3), data_to=datetime(2017, 3, 3))
    assert output == []
    output = a_slice.get(data_from=datetime(2017, 3, 5))
    assert output == [[np.datetime64(datetime(2017, 3, 5)), 2], \
                      [np.datetime64(datetime(2017, 3, 6)), 3], \
                      [np.datetime64(datetime(2017, 3, 7)), 4], \
                      [np.datetime64(datetime(2017, 3, 8)), 5]]
    output = a_slice.get(data_from=datetime(2017, 3, 11))
    assert output == []