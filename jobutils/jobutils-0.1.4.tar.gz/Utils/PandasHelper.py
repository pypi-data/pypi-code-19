#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd

from Utils import decorator_f

__author__ = "laurynas@joberate.com"


def create_empty_data_frame(index=[], columns=[]):
    """

    :param index:
    :param columns:
    :return:
    """
    return pd.DataFrame(index=index, columns=columns)


def create_data_frame(data, columns=[], index=[]):
    """

    :param index:
    :param columns:
    :return:
    """
    if len(index) == 0:
        index = range(0, len(data))

    return pd.DataFrame(data=data, index=index, columns=columns)

def create_series(data=[]):
    """

    :param data:
    :return:
    """
    return pd.Series(data=data)

def get_closest_index(values, value):
    """
    Retrieves the closest index to specified value
    :param values: List of column values
    :param value:
    :return: closest value index identifier
    """
    values = np.array(values)
    return np.argmin([np.abs(values - value)])

def create_data_frame_from_dictionary(dictionary):
    """
    :param dictionary: Python Dictionary object
    :return: Pandas DataFrame object
    """
    data_frame = pd.DataFrame.from_dict(dictionary.items()).transpose()
    data_frame.columns = data_frame.loc[0]
    return data_frame.ix[1:]

def interpolate_missing_values(data_frame, method='pad'):
    """
    Interpolates missing values in Pandas DataFrame object
    :param data_frame: Pandas DataFrame object
    :param method: specifies how to fill missing values; Possible values - {pda , backfill, bfill, pad, ffill, None}
    :return: Pandas DataFrame object with filled missing values
    """
    return data_frame.fillna(method=method)

def merge_data_frames(data_frames):
    """
    Merges list of Pandas DataFrame objects
    :param data_frames:
    :return:
    """
    dfs = pd.concat(data_frames)
    dfs.index = range(0, len(dfs))
    return dfs

@decorator_f
def import_data_frame(path):
    """

    :param path:
    :return:
    """
    return pd.read_csv(path, low_memory=False)

@decorator_f
def export_data_frame_to_matrix_dictionary(data, fraction=1):
    """

    :param data:
    :param fraction:
    :return:
    """
    if len(data) > 0:
        return data.sample(frac=fraction).as_matrix().tolist()

    return []

@decorator_f
def export_data_frame_columns(data):
    """

    :param data:
    :return:
    """
    if len(data) > 0:
        return data.columns.values.tolist()

    return []

@decorator_f
def try_get_value(data, column):
    """

    :param data:
    :param column:
    :return:
    """
    if column in data:
        return data[column]

    return 0

@decorator_f
def retain_columns(data, columns):
    """
    Returns specified columns from Pandas DataFrame object
    :param data:
    :param columns:
    :return:
    """
    if len(data) > 0:
        return data[columns]

    return create_empty_data_frame()

@decorator_f
def export_data_frame_to_json(data):
    """

    :param data:
    :return:
    """
    if len(data) > 0:
        return data\
            .to_json(date_format='iso',
                     orient='records',
                     force_ascii=False)\
            .replace('\"', '\'')

    return []

@decorator_f
def export_data_frame_to_dictionary(data):
    """

    :param data:
    :return:
    """
    data = data.replace(np.nan, -1)

    if len(data) > 0:
        return data.to_dict(orient='records')

    return []

@decorator_f
def select_data_as_scalar_absolute_index_data_frame(data, condition, selected_column=None):
    """
    Returns single value from Pandas DataFrame given the absolute index
    :param data:
    :param condition:
    :param selected_column:
    :return:
    """
    if selected_column is None:
        selected_column = data.columns

    return data.at[condition, selected_column]

@decorator_f
def select_data_as_scalar_relative_index_data_frame(data, condition, selected_column=None):
    """
    Returns single value from Pandas DataFrame given the relative index
    :param data:
    :param condition:
    :param selected_column:
    :return:
    """
    if selected_column is None:
        selected_column = data.columns

    return data.iat[condition, data.columns.get_loc(selected_column)]

@decorator_f
def select_data_as_vector_absolute_index_series(data, condition):
    """
    Returns vector (list of values) from Pandas Series object given the absolute index
    :param data:
    :param condition:
    :return:
    """
    return data.loc[condition]

@decorator_f
def select_data_as_scalar_absolute_index_series(data, index):
    """
    Returns vector (list of values) from Pandas Series object given the absolute index
    :param data:
    :param index:
    :return:
    """
    return data.loc[index]

@decorator_f
def select_data_as_vector_absolute_index_data_frame(data, condition, selected_columns=None):
    """
    Returns vector (list of values) from Pandas DataFrame given the absolute index
    :param data:
    :param condition:
    :param selected_columns:
    :return:
    """
    if selected_columns is None:
        selected_columns = data.columns

    return data.loc[condition, selected_columns]

@decorator_f
def select_data_as_vector_relative_index_data_frame(data, condition, selected_columns=None):
    """
    Returns vector (list of values) from Pandas DataFrame given the relative index
    :param data:
    :param condition:
    :param selected_columns:
    :return:
    """
    if selected_columns is None:
        selected_columns = data.columns

    return data.iat[condition, selected_columns]


def get_mode(data):
    """
    Returns mode of Pandas Series object
    :return:
    """
    data = data.dropna()
    modes = data.mode()
    if modes.empty:
        return np.nan

    return modes[0]

@decorator_f
def assign_value_series_scalar(data, value, index):
    """
    Assigns single value to Pandas Series object
    :param data:
    :param value:
    :param index:
    """
    data.set_value(index, value)

@decorator_f
def assign_value_dataframe_scalar(data, value, index=None, columns=None):
    """
    Assigns single to Pandas DataFrame object
    :param data: Pandas DataFrame object
    :param value:
    :param columns: Defines columns for which values will be set
    :param index: Defines index of assigned values
    """
    if columns is None:
        columns = []

    if index is None:
        index = []

    data.set_value(index, columns, value)

@decorator_f
def assign_value_dataframe_vector(data, values, index=None, columns=None):
    """
    Assigns vector value (list of values) to Pandas DataFrame object
    :param data: Pandas DataFrame object
    :param values:
    :param columns: Defines columns for which values will be set
    :param index: Defines index of assigned values
    """
    if columns is None:
        columns = data.columns

    if index is None:
        index = data.index

    if isinstance(values, pd.Series) or isinstance(values, pd.DataFrame):
        data.set_value(index, columns, values)
    else:
        data.set_value(index, columns, values)

@decorator_f
def convert_list_to_data_frame(data):
    """

    :param data:
    :return:
    """
    return pd.DataFrame(data)

@decorator_f
def convert_to_date(series):
    """

    :param series:
    :return:
    """
    return pd.to_datetime(series)

@decorator_f
def create_data_frame_from_list(records):
    """

    :param records:
    :return:
    """
    return pd.DataFrame.from_records(records)

@decorator_f
def factorize_string_series(data):
    """
    Converts list of strings into list of factors
    :param data:
    :return:
    """
    return pd.factorize(data)


def generate_quantile_intervals(n):
    """
    
    :param n: 
    :return: 
    """
    intervals = []
    step = 1/(n*1.0)

    for i in range(0, n):
        intervals.append({'low': round(i * step, 1), 'high': round((i + 1) * step, 1)})

    return intervals


def generate_absolute_intervals(series, intervals):
    """
    
    :param series: 
    :param intervals: 
    :return: 
    """
    result = []
    for interval in intervals:
        result.append({'low': series.quantile(interval['low']),
                       'high': series.quantile(interval['high'])})

    return result


def convert_continuous_to_ordinal(series, n, labels=[]):
    """
    
    :param series: 
    :param n: 
    :param labels: 
    :return: 
    """
    if len(labels) != n:
        raise

    df = pd.DataFrame(data={'values': series, 'bin': range(0, len(series))})

    relative_intervals = generate_quantile_intervals(n)
    quantile_intervals = generate_absolute_intervals(series, relative_intervals)

    for i in range(0, len(quantile_intervals)):
        condition = (df['values'] >= quantile_intervals[i]['low'])&(df['values'] <= quantile_intervals[i]['high'])
        if len(labels) > 0:
            df.loc[condition, 'bin'] = labels[i]
        else:
            df.loc[condition, 'bin'] = i

    return df['bin']