from enum import Enum
from datetime import datetime

import numpy as np
import pandas as pd


class DifferenceType(Enum):
    file_not_found = 1
    column_not_found = 2
    duplicated_keys = 3
    missing_keys = 4


class DiffTask(object):
    def __init__(self, base_file_name, reg_file_name, key_list, ignored_columns=list()):
        self.base_file = base_file_name
        self.reg_file = reg_file_name
        self.keys = key_list
        self.differences = list()
        self.ignored_columns = ignored_columns
        self.run_time = None

    def compute(self):
        self.run_time = datetime.now()
        self.differences = list()
        try:
            base_df = pd.read_csv(self.base_file)
        except Exception as ex:
            self.differences.append(MissingDifference(DifferenceType.file_not_found, ex, True))
            return self.differences
        try:
            reg_df = pd.read_csv(self.reg_file)
        except Exception as ex:
            self.differences.append(MissingDifference(DifferenceType.file_not_found, ex, False))
            return self.differences

        if len(self.ignored_columns) != 0:
            drop_columns(base_df, ignored_columns=self.ignored_columns)
            drop_columns(reg_df, ignored_columns=self.ignored_columns)

        self.differences.extend(col_diff(base_df, reg_df))

        results = duplicate_keys(base_df, self.keys)
        for result in results:
            self.differences.append(DuplicationDifference(result.type, result.keys, True, result.line_number))
        if len(results) != 0:
            base_df.drop_duplicates(subset=self.keys, keep='first', inplace=True)
        results = duplicate_keys(reg_df, self.keys)
        for result in results:
            self.differences.append(DuplicationDifference(result.type, result.keys, False, result.line_number))
        if len(results) != 0:
            reg_df.drop_duplicates(subset=self.keys, keep='first', inplace=True)

        self.differences.extend(missing_keys(base_df, reg_df, self.keys))
        self.differences.extend(data_diff(base_df, reg_df, self.keys))

        return self.differences

    def summary(self):
        return {'base_file': self.base_file,
                'reg_file': self.reg_file,
                'run_time': self.run_time,
                'keys': self.keys,
                'ignored_columns': self.ignored_columns,
                'differences': [diff.__repr__() for diff in self.differences]}


def drop_columns(df, ignored_columns):
    for col in df.columns:
        if col in ignored_columns:
            df.drop([col], axis=1, inplace=True)


def col_diff(base_df, reg_df):
    results = list()
    for col in base_df.columns:
        if col not in reg_df:
            results.append(MissingDifference(DifferenceType.column_not_found, col, False))
    for col in reg_df.columns:
        if col not in base_df:
            results.append(MissingDifference(DifferenceType.column_not_found, col, True))
    return results


def duplicate_keys(df, keys):
    results = list()
    duplicated = df.duplicated(subset=keys, keep='first')
    duplicated = duplicated[duplicated]
    for index in duplicated.index:
        results.append(DuplicationDifference(DifferenceType.duplicated_keys,
                                             df[keys].ix[index].tolist(),
                                             None,
                                             index + 1))
    return results


def missing_keys(base_df, reg_df, keys):
    results = list()
    base_df = base_df.set_index(keys=keys)
    reg_df = reg_df.set_index(keys=keys)
    diff = base_df.index.difference(reg_df.index)
    results.extend([MissingDifference(type=DifferenceType.missing_keys,
                                      data=sanitize(i),
                                      base_is_missing=False) for i in diff])
    diff = reg_df.index.difference(base_df.index)
    results.extend([MissingDifference(type=DifferenceType.missing_keys,
                                      data=sanitize(i),
                                      base_is_missing=True) for i in diff])
    return results


def data_diff(base_df, reg_df, keys):
    results = list()
    columns_of_interest = set(base_df.columns.tolist()).intersection(reg_df.columns.tolist())
    for key in keys:
        columns_of_interest.remove(key)
    base_df = base_df.set_index(keys=keys)
    reg_df = reg_df.set_index(keys=keys)
    base_df = base_df.rename(columns={key:'base_' + key for key in base_df.columns}, inplace=False)
    reg_df = reg_df.rename(columns={key:'reg_' + key for key in reg_df.columns}, inplace=False)
    joint_df = pd.concat([base_df, reg_df], axis=1, join='inner')
    for column in columns_of_interest:
        base_col = 'base_' + column
        reg_col = 'reg_' + column
        joint_df['diff_' + column] = np.where(joint_df[base_col] == joint_df[reg_col], True, False)
        differences = joint_df[~joint_df['diff_' + column]]
        if not differences.empty:
            differences = differences.apply(lambda r: DataDifference(keys=r.name,
                                                                     column=column,
                                                                     base_value=r[base_col],
                                                                     reg_value=r[reg_col]), axis=1).tolist()
            results.extend(differences)
    return results


def sanitize(keys):
    if type(keys) == tuple:
        return list(keys)
    elif type(keys) == list:
        return keys
    else:
        return [keys]


class DuplicationDifference(object):
    def __init__(self, type, keys, is_base, line_number):
        self.type = type
        self.keys = sanitize(keys)
        self.is_base = is_base
        self.line_number = line_number

    def __repr__(self):
        return {'type': str(self.type),
                'keys': self.keys,
                'file': 'base' if self.is_base else 'reg',
                'line_number': self.line_number}


class MissingDifference(object):
    def __init__(self, type, data, base_is_missing):
        self.type = type
        self.data = data
        self.base_is_missing = base_is_missing

    def __repr__(self):
        return {'type': str(self.type),
                'data': self.data,
                'file': 'base' if self.base_is_missing else 'reg'}


class DataDifference(object):
    def __init__(self, keys, column, base_value, reg_value):
        self.keys = sanitize(keys)
        self.column = column
        self.base_value = base_value
        self.reg_value = reg_value

    def __repr__(self):
        return {'type': 'data_mismatch',
                'keys': self.keys,
                'column': self.column,
                'base_value': self.base_value,
                'reg_value': self.reg_value}
