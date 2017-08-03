"""
Functions related to reading csv files in DataFrame objects.
Tests for wide formatted data and converts to long.
"""

import csv
import pandas as pd
# ------------------------------------------------------------------------------

def infer_type(row):
    if all(s.isnumeric() for s in row):
        return list(map(int, row))
    elif all('.' in s for s in row):
        if all(s.replace('.','',1).isnumeric() for s in row):
            return list(map(float, row))
    return row


def read_wide(csv_path):
    with open(csv_path, 'r') as csv_file:
        datareader = csv.reader(csv_file)
        rows = {row[0]:infer_type(row[1:]) for row in datareader}
    return rows


def is_wide(df):
    # check for any numeric column names
    if set(map(type, df.columns)) & set((int, float)):
        return True
    elif not df.select_dtypes(exclude=['object']).columns.any():
        return True
    else:
        return False


def load(csv_path):
    df = pd.read_csv(csv_path, index_col=None)

    if is_wide(df):
        df = pd.DataFrame(read_wide(csv_path))

    if df.columns.contains('$DATE'):
        df.index = pd.to_datetime(df['$DATE'])
        del df['$DATE']

    return df
