from StringIO import StringIO
from datetime import datetime

import pytest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

import tss.utils as utils
from tss.models import Slice, SparseSlice, Series


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