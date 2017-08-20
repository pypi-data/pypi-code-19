import os
from StringIO import StringIO

import pandas as pd
import pytest

from . import TEST_DATA_DIR


@pytest.fixture
def base_file_name():
    return os.path.join(TEST_DATA_DIR, 'base.csv')


@pytest.fixture
def some_df():
    input_data = StringIO("""col1,col2,col3
1,2,3
4,5,6
7,8,9
""")
    df = pd.read_csv(input_data, sep=",")
    return df


@pytest.fixture
def empty_df():
    return pd.DataFrame()
