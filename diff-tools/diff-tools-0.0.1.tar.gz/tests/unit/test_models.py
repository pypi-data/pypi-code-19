from StringIO import StringIO

from mock import patch, sentinel
import pandas as pd

import diff.tools.models as models

from . import for_all


def test_can_handle_non_exist_base_file():
    task = models.DiffTask("non_exist_base_file", "non_exist_reg_file", [], [])
    results = task.compute()
    assert len(results) == 1
    diff = results[0]
    assert type(diff) == models.MissingDifference
    assert diff.type == models.DifferenceType.file_not_found
    assert diff.base_is_missing


def test_can_handle_non_exist_reg_file(base_file_name):
    task = models.DiffTask(base_file_name, "non_exist_reg_file", [], [])
    results = task.compute()
    assert len(results) == 1
    diff = results[0]
    assert type(diff) == models.MissingDifference
    assert diff.type == models.DifferenceType.file_not_found
    assert not diff.base_is_missing


def test_compute(base_file_name):
    with patch('diff.tools.models.col_diff') as col_diff, \
         patch('diff.tools.models.duplicate_keys') as duplicate_keys, \
         patch('diff.tools.models.missing_keys') as missing_keys, \
         patch('diff.tools.models.data_diff') as data_diff:
        col_diff.return_value = [sentinel.col_diff]
        duplicate_keys.return_value = []
        missing_keys.return_value = [sentinel.missing_keys]
        data_diff.return_value = [sentinel.data_diff]
        task = models.DiffTask(base_file_name, base_file_name, [], [])
        results = task.compute()
        col_diff.assert_called_once()
        duplicate_keys.assert_called()
        missing_keys.assert_called_once()
        data_diff.assert_called_once()
        assert duplicate_keys.call_count == 2
        assert sentinel.col_diff in results
        assert sentinel.missing_keys in results
        assert sentinel.data_diff in results


def test_col_diff_handles_matching_base_reg_columns(some_df):
    results = models.col_diff(some_df, some_df)
    assert len(results) == 0


def test_col_diff_handles_base_having_more_cols(some_df, empty_df):
    results = models.col_diff(some_df, empty_df)
    assert len(results) == len(some_df.columns)
    assert for_all(results, lambda r: not r.base_is_missing)
    assert for_all(results, lambda r: r.type == models.DifferenceType.column_not_found)


def test_col_diff_handles_reg_having_more_cols(some_df, empty_df):
    results = models.col_diff(empty_df, some_df)
    assert len(results) == len(some_df.columns)
    assert for_all(results, lambda r: r.base_is_missing)
    assert for_all(results, lambda r: r.type == models.DifferenceType.column_not_found)


def test_find_duplicate_keys_when_there_is_no_duplicate_keys():
    input_data = StringIO("""col1,col2,col3
1,2,3
4,5,6
7,8,9
""")
    df = pd.read_csv(input_data, sep=",")
    results = models.duplicate_keys(df, ["col1"])
    assert len(results) == 0


def test_find_duplicate_keys_handles_single_key_difference():
    input_data = StringIO("""col1,col2,col3
c1,2,3
c1,5,6
c1,8,9
""")
    df = pd.read_csv(input_data, sep=",")
    results = models.duplicate_keys(df, ["col1"])
    assert len(results) == 2
    result = results[0]
    assert type(result) == models.DuplicationDifference
    assert result.type == models.DifferenceType.duplicated_keys
    assert result.keys == ['c1']
    assert result.is_base is None
    assert result.line_number == 2
    result = results[1]
    assert type(result) == models.DuplicationDifference
    assert result.type == models.DifferenceType.duplicated_keys
    assert result.keys == ['c1']
    assert result.is_base is None
    assert result.line_number == 3


def test_find_duplicate_keys_handles_multi_keys_difference():
    input_data = StringIO("""col1,col2,col3
1,2,3
1,2,6
7,2,9
""")
    df = pd.read_csv(input_data, sep=",")
    results = models.duplicate_keys(df, ["col1", "col2"])
    assert len(results) == 1
    result = results[0]
    assert type(result) == models.DuplicationDifference
    assert result.type == models.DifferenceType.duplicated_keys
    assert result.keys == [1, 2]
    assert result.is_base is None


def test_data_diff_when_no_diff():
    input_base_data = StringIO("""col1,col2,col3
c1,2,3
c2,5,6
c3,8,9
""")
    base_df = pd.read_csv(input_base_data, sep=",")
    results = models.data_diff(base_df, base_df, ['col2'])
    assert len(results) == 0


def test_single_key_data_difference():
    input_base_data = StringIO("""col1,col2,col3
c1,2,3
c2,5,6
c3,8,9
""")
    base_df = pd.read_csv(input_base_data, sep=",")
    input_reg_data = StringIO("""col1,col2,col3
c1,2,3
c1,5,6
c1,8,9
""")
    reg_df = pd.read_csv(input_reg_data, sep=",")
    results = models.data_diff(base_df, reg_df, ['col2'])
    assert len(results) == 2

    result = results[0]
    assert type(result) == models.DataDifference
    assert result.keys == [5]
    assert result.column == 'col1'
    assert result.base_value == 'c2'
    assert result.reg_value == 'c1'

    result = results[1]
    assert type(result) == models.DataDifference
    assert result.keys == [8]
    assert result.column == 'col1'
    assert result.base_value == 'c3'
    assert result.reg_value == 'c1'


def test_multi_keys_data_difference():
    input_base_data = StringIO("""col1,col2,col3
c1,2,3
c2,5,6
c3,8,9
""")
    base_df = pd.read_csv(input_base_data, sep=",")
    input_reg_data = StringIO("""col1,col2,col3
c1,2,3
c2,5,6
c3,8,10
""")
    reg_df = pd.read_csv(input_reg_data, sep=",")
    results = models.data_diff(base_df, reg_df, ['col1', 'col2'])
    assert len(results) == 1

    result = results[0]
    assert type(result) == models.DataDifference
    assert result.keys == ['c3', 8]
    assert result.column == 'col3'
    assert result.base_value == 9
    assert result.reg_value == 10


def test_drop_columns(some_df):
    columns = some_df.columns
    list = [columns[0]]
    models.drop_columns(some_df, list)
    assert len(some_df.columns) == (len(columns) - 1)
