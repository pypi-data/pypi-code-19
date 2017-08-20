from StringIO import StringIO
from datetime import datetime

import pytest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

import tss.utils as utils
from tss.models import Slice, SparseSlice, Series


def test_add_series(db, series):
    result = utils.add_series('test', '1d', ['col1'], db)
    assert result.id is not None
    assert result.collection == series
    assert result.name == 'test'
    assert result.frequency == '1d'
    assert result.columns == ['col1']
    assert result.slices == {}
    
    
def test_add_series_errors_when_frequency_is_not_valid(db):
    with pytest.raises(ValueError) as error:
        utils.add_series('test', 'XX', [], db)
    assert error.value.message == 'frequency is not valid'
    

def test_get_series_when_empty(db):
    results = utils.get_series(db)
    assert len(results) == 0
    

def test_get_series_by_id(db, series):
    s1 = utils.add_series('test', '1d', [], db)
    results = utils.get_series(db, id=s1.id)
    assert len(results) == 1
    result = results[0]
    assert s1.name == result.name
    assert s1.id == result.id
    assert s1.frequency == result.frequency
    assert s1.columns == result.columns
    assert s1.slices == result.slices
    
    
def test_get_series_by_invalid_id(db, series):
    results = utils.get_series(db, id='123456')
    assert results == []
    

def test_get_series_by_non_existing_id(db, series):
    results = utils.get_series(db, id='58b0b8b9f4a6b002cbb14ba9')
    assert results == []


def test_get_slices(db):
    slices = []
    assert utils._get_slices(db=db, slices=slices) == []
    assert utils._get_slices(db=db) == []   
    t = datetime.now()
    slices = [{'start': t, 'num_of_samples':100, 'is_sparse': False}, 
              {'start': t, 'num_of_samples':1, 'id': 123, 
               'is_sparse': True}]
    results = utils._get_slices(db=db, slices=slices)
    assert len(results) == 2
    result = results[0]
    assert result.db == db
    assert result.start == t
    assert result.num_of_samples == 100
    assert result.id is None
    assert type(result) == Slice
    assert result.is_sparse == False
    result = results[1]
    assert result.db == db
    assert result.start == t
    assert result.num_of_samples == 1
    assert result.id == 123
    assert type(result) == SparseSlice
    assert result.is_sparse == True


def test_clear_all_when_empty(db, series, data):
    results = utils._clear_all(db)
    assert len(results) == 2
    assert 'series' in results
    assert 'data' in results
    assert results['series'] == 0
    assert results['data'] == 0
    

def test_clear_all_when_there_are_some_data(db, series, data):
    for _ in range(3):
        series.insert({})
    for _ in range(4):
        data.insert({})
    results = utils._clear_all(db)
    assert len(results) == 2
    assert 'series' in results
    assert 'data' in results
    assert results['series'] == 3
    assert results['data'] == 4
    
    
def test_create_with_sparse_slices_from_df(db, series, data):
    input_data=StringIO("""col1,col2,col3
1,2,3
4,5,6
7,8,9
""")
    df = pd.read_csv(input_data, sep=",")
    df['time'] = pd.Series([np.datetime64(datetime(2017, 3, 8)),
                            np.datetime64(datetime(2017, 3, 9)),
                            np.datetime64(datetime(2017, 3, 10))])
    df.set_index(['time'], inplace=True)
    result = utils.create_with_sparse_slices_from_df(df, 'test1', '1d', 1, db)
    assert result is not None
    assert isinstance(result, Series)
    assert len(result.slices) == 3
    assert type(result) == Series
    assert series.find({}).count() == 1
    assert data.find({}).count() == 3
    series_docs = [s for s in series.find({})]
    data_docs = [d for d in data.find({})]
    df_new = result.get()
    assert_frame_equal(df, df_new, check_dtype=False)
