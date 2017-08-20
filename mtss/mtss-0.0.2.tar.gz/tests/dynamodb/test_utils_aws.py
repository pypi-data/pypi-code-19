from StringIO import StringIO
from datetime import datetime

import pytest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

import tss.utils_aws as utils
from tss.models_aws import Series, SparseSlice


def test_add_series(series):
    result = utils.add_series('test', '1d', ['col1'])
    assert result.collection == series
    assert result.name == 'test'
    assert result.frequency == '1d'
    assert result.columns == ['col1']
    assert result.slices == {}


def test_add_series_errors_when_frequency_is_not_valid(db):
    with pytest.raises(ValueError) as error:
        utils.add_series('test', 'XX', [], db)
    assert error.value.message == 'frequency is not valid'


def test_get_series():
    utils.add_series('test_get_series', '1s', ['col1'], scope='test')
    series = utils.get_series('test', 'test_get_series')
    assert series.scope == 'test'
    assert series.name == 'test_get_series'
    assert series.frequency == '1s'
    assert series.columns == ['col1']
    assert series.slices == {}


def test_get_slices(db):
    t = datetime.now()
    slices = [{'start': t, 'num_of_samples': 100, 'is_sparse': False},
              {'start': t, 'num_of_samples': 1, 'id': 123,
               'is_sparse': True}]
    results = utils._get_slices(db=db, slices=slices)
    assert len(results) == 2
    result = results[0]
    assert result.db == db
    assert result.start == t
    assert result.id is None
    assert type(result) == SparseSlice
    assert result.is_sparse
    result = results[1]
    assert result.db == db
    assert result.start == t
    assert result.id == 123
    assert type(result) == SparseSlice
    assert result.is_sparse


def test_create_with_sparse_slices_from_df(db):
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
    result = utils.create_with_sparse_slices_from_df(df, 'test_scope', 'test_create_with_sparse_slices_from_df', '1d', 1, db)
    assert result is not None
    assert isinstance(result, Series)
    assert len(result.slices) == 3
    assert type(result) == Series
    df_new = result.get()
    assert_frame_equal(df, df_new, check_dtype=False)


def test_delete_series_with_slices(db):
    input_data = StringIO("""col1,col2,col3
    1,2,3
    4,5,6
    7,8,9
    """)
    df = pd.read_csv(input_data, sep=",")
    df['time'] = pd.Series([np.datetime64(datetime(2017, 3, 8)),
                            np.datetime64(datetime(2017, 3, 9)),
                            np.datetime64(datetime(2017, 3, 10))])
    df.set_index(['time'], inplace=True)
    result = utils.create_with_sparse_slices_from_df(df, 'test_scope', 'test_delete_series_with_slices', '1d',
                                                     1, db)
    assert result is not None
    result.delete()
    with pytest.raises(KeyError):
        utils.get_series('test_scope', 'test_delete_series_with_slices', db).get()


def test_load_series(db):
    input_data = StringIO("""col1,col2,col3
    1,2,3
    4,5,6
    7,8,9
    """)
    df = pd.read_csv(input_data, sep=",")
    df['time'] = pd.Series([np.datetime64(datetime(2017, 3, 8)),
                            np.datetime64(datetime(2017, 3, 9)),
                            np.datetime64(datetime(2017, 3, 10))])
    df.set_index(['time'], inplace=True)
    result = utils.create_with_sparse_slices_from_df(df, 'test_scope', 'test_load_series', '1d', 1, db)
    assert result is not None
    assert isinstance(result, Series)
    assert len(result.slices) == 3
    assert type(result) == Series
    df_new = utils.get_series('test_scope', 'test_load_series', db).get()
    assert_frame_equal(df, df_new, check_dtype=False)
