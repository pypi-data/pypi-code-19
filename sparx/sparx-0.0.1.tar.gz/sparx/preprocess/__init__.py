"""
    Module: Data Preprocessing Models
    Project: Sparx
    Authors: Bastin Robins. J
    Email : robin@cleverinsight.com
"""
from datetime import datetime
from urllib import urlencode
import datetime as dt
import re
import logging
import itertools
import dateutil
import numpy as np
import pandas as pd
import blaze as bz
from sparx.preprocess.stopwords import stopwords
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import StandardScaler
import dateutil.parser as parser
from geopy.geocoders import Nominatim
from scipy import stats



def geocode(address):
    ''' Return full address, latitude and longitude of give address string

    Parameters:
    -----------
        address: str
            Enter a dictionary of address whose latitude and longitude
            should be returned

    Usage:
    ------
        >>> geocode("172 5th Avenue NYC")
        >>> {'latitude': 40.74111015, 'adress': '172, 5th Avenue, Flatiron,
         Manhattan, Manhattan Community Board 5, New York County, NYC,
         New York, 10010, United States of America',
        'longitude': -73.9903105}

    '''
    geolocator = Nominatim()
    location = geolocator.geocode(address)
    return dict(address=location.address, latitude=location.latitude,\
        longitude=location.longitude)


def unique_value_count(data):
    '''
    return unique value count of each column as dict mapped

    Parameters:
    -----------
        column_name: str
            Enter the column for checking unique values

    Usage:
    ------
        >>> unique_value_count(data['name'])
        >>> {'gender': {'Male': 2, 'Female': 6},
        'age': {32: 2, 34: 2, 35: 1, 37: 1, 21: 1, 28: 1},
        'name': {'Neeta': 1, 'vandana': 2, 'Amruta': 1, 'Vikrant': 2,
        'vanana': 1, 'Pallavi': 1}}

    '''
    response = {}
    for col in data.columns:
        response[col] = dict(data[col].value_counts())
    return response


def unique_identifier(data):
    ''' Return a list of columns from the dataframe which
    consist of unique identifiers

    Parameters:
    -----------
        data: pandas.core.Dataframe
            complete dataframe

    Examples
    --------
    Usage::
        >>> unique_identifier(pd.Dataframe)
        >>> ['age', 'id']
    '''
    unique_col = []
    for col in data.columns:
        if len(data[col].unique()) == data[col].size:
            unique_col.append(col)
    return unique_col


def date_split(datestring):
    ''' Return a dictionary of year, month,day, hour, minute and second

    Parameters:
    -----------

        datestring: str
            Enter the datetime string


    Usage:
    ------

        >>> date_split("march/1/1980")
        >>> {'second': '00', 'hour': '00', 'year': '1980', 'day': '01',
        'minute': '00', 'month': '03'}

    '''


    date, time = str(parser.parse(datestring)).split(' ')
    date = date.split('-')
    time = time.split(':')
    return dict(year=date[0], month=date[1], day=date[2],\
     hour=time[0], minute=time[1], second=time[2])


def is_categorical(dataframe):
    ''' comment '''
    if dataframe.dtypes == 'object':
        return True
    else:
        return False


def count_missing(data):
    ''' Return the count of missing values

    Paratmers:
    ----------
        data: pandas.core.series
            given a column in pandas dataframe
    Usage:
    -------
        >>> count_missing(df['col_name'])
        >>> 0

    '''
    return data.isnull().sum()


def dict_query_string(query_dict):
    ''' Return a string which is the query formed using the given dictionary
    as parameter

    Parameters
    ----------
        query_dict: Dict
            Dictionary of keys and values


    Usage
    -----
        # Input query string
        query = {'name': 'Sam', 'age': 20 }

        >>> dict_query_string(query)
        >>> name=Same&age=20
    '''

    return urlencode(query_dict)


def describe(dataframe, col_name):
    ''' Return the basic description of an column in a pandas dataframe
    check if the column is an interger or float type

    Parameters:
    -----------
        dataframe: pandas dataframe
        col_name: str
            any one column name in the dataframe passed
    Usage:
    ------
        >>> describe(dataframe, 'Amount')
        >>> {'min': 0, 'max': 100, 'mean': 50, 'median': 49 }

    '''

    try:
        return dict(min=dataframe[col_name].min(), max=dataframe[col_name].max(),\
         mean=dataframe[col_name].mean(), median=dataframe[col_name].median())

    except (ValueError,      # Values that cannot be converted into dates
            TypeError,       # Values that cannot be converted into dates
            AttributeError,  # Long ints do not have a .read attribute
            OverflowError):  # Long ints like mobile numbers raise this
        return False


def encode(data):
    ''' Return a clean dataframe which is initially converted into utf8 format
    and all categorical variables are converted into numeric labels also each
    label encoding classes as saved into a dictionary now a tuple of first
    element is dataframe and second is the hash_map

    Parameters:
    ------------
        data : pandas dataframe

    Usage:
    ------
        >>> encode(pd.DataFrame())

    '''
    # Remove all the ascii unicodes
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    # Instantiate the LabelEncoder instance
    label = LabelEncoder()

    # One shot hot encoding if its categorical variable
    hash_map = {}
    date_columns = []
    for col in data.columns:
        if data[col].dtypes == 'object':
            hash_map[col] = dict(zip(label.fit_transform(data[col].unique()),\
             data[col].unique()))
            label.fit(data[col].values)
            data[col] = label.transform(data[col])

    return (data, hash_map)


def is_date(series):
    '''
    Returns ``True`` if the first 1000 non-null values in a ``series`` are
    parseable as dates
    Parameters
    ----------
    series : Pandas Series
    Examples
    --------
    Usage::
        is_date(pd.Series(['Jul 31, 2009', '2010-01-10', None]))
        >>> True
        is_date(pd.Series(['Jul 31, 2009', '2010-101-10', None]))
        >>> False
        is_date(pd.Series(pd.date_range('1/1/2011', periods=72, freq='H')))
        >>> True
    '''

    series = series.dropna()[:1000]
    if len(series) == 0:
        return False
    if series.apply(lambda v: issubclass(type(v), dt.datetime)).all():
        return True
    try:
        series.apply(dateutil.parser.parse)
    except (ValueError,      # Values that cannot be converted into dates
            TypeError,       # Values that cannot be converted into dates
            AttributeError,  # Long ints do not have a .read attribute
            OverflowError):  # Long ints like mobile numbers raise this
        return False
    return True


def groupmeans(data, groups, numbers, cutoff=.01, quantile=.95, min_size=None):
    ''' Yields the significant differences in average between every pair of
    groups and numbers.

    Parameters
    ----------
    data : blaze data object
    groups : non-empty iterable containing category column names in data
    numbers : non-empty iterable containing numeric column names in data
    cutoff : ignore anything with prob > cutoff.
        cutoff=None ignores significance checks, speeding it up a LOT.
    quantile : number that represents target improvement. Defaults to .95.
        The ``diff`` returned is the % impact of everyone moving to the 95th
        percentile
    min_size : each group should contain at least min_size values.
        If min_size=None, automatically set the minimum size to
        1% of the dataset, or 10, whichever is larger.
    '''

    if min_size is None:
        # compute nrows, bz.compute(data.nrows) doesn't work for sqlite
        min_size = max(bz.into(int, data.nrows) / 100, 10)

    # compute mean of each number column
    means = {col: bz.into(float, data[col].mean()) for col in numbers}
    # pre-create aggregation expressions (mean, count)
    agg = {number: bz.mean(data[number]) for number in numbers}
    for group in groups:
        agg['#'] = data[group].count()
        ave = bz.by(data[group], **agg).sort('#', ascending=False)
        ave = bz.into(pd.DataFrame, ave)
        ave.index = ave[group]
        sizes = ave['#']
        # Each group should contain at least min_size values
        biggies = sizes[sizes >= min_size].index
        # ... and at least 2 groups overall, to compare.
        if len(biggies) < 2:
            continue
        for number in numbers:
            if number == group:
                continue
            sorted_cats = ave[number][biggies].dropna().sort_values()
            if len(sorted_cats) < 2:
                continue
            sohi = sorted_cats.index[-1]
            solo = sorted_cats.index[0]

            # If sorted_cats.index items are of numpy type, then
            # convert them to native type, skip conversion for unicode, str
            # See https://github.com/blaze/blaze/issues/1461
            if isinstance(solo, np.generic):
                solo, sohi = solo.item(), sohi.item()

            low = bz.into(list, data[number][data[group] == solo])
            high = bz.into(list, data[number][data[group] == sohi])

            _, prob = ttest_ind(
                np.ma.masked_array(low, np.isnan(low)),
                np.ma.masked_array(high, np.isnan(high))
            )
            if prob > cutoff:
                continue

            yield ({
                'group': group,
                'number': number,
                'prob': float(prob),
                'gain': sorted_cats.iloc[-1] / means[number] - 1,
                'biggies': ave.ix[biggies][number].to_dict(),
                'means': ave[[number, '#']].sort_values(by=number).reset_index().to_dict(
                    orient='records'),
            })


def has_keywords(series, sep=' ', thresh=2):
    '''
    Returns ``True`` if any of the first 1000 non-null values in a string
    ``series`` are strings that have more than ``thresh`` =2 separators
    (space, by default) in them
    Parameters
    ----------
    series : pd.Series
        Must be a string series. ``series.str.count()`` should be valid.
    sep : str
        Separator within the words. Defaults to ``' '`` space.
    thresh : int
        Threshold number of times a separator should occur in the word.
        Defaults to 2.
    Examples
    --------
    Usage::
        series = pd.Series(['Curd ', 'GOOG APPL MS', 'A B C', 'T Test is'])
        has_keywords(series)
        # False
        has_keywords(series, thresh=1)
        # True
    '''
    return (series.dropna()[:1000].str.count(sep) > thresh).any()

def types(data):
    '''
    Returns the column names in groups for the given DataFrame
    Parameters
    ----------
    data : Blaze DataFrame
    Returns
    -------
    dict : dictionary of data-types
        | groups : categorical variables that you can group by
        | dates : date parseable columns (subset of groups)
        | numbers : numerical variables that you can average
        | keywords : strings with at least two spaces
    Examples
    --------
    Consider this DataFrame::
            A   B     C           D
        0   1   2   A B C D    Jul 31, 20
        1   2   3   World is   2010-11-10
    Running ``types(data)`` returns::
        {'dates': ['D'],
         'groups': ['C', 'D'],
         'keywords': ['C'],
         'numbers': ['A', 'B']}
    '''

    typ = {}
    typ['numbers'] = get_numeric_cols(data.dshape)
    typ['groups'] = list(set(data.fields) - set(typ['numbers']))
    typ['dates'] = [group for group in typ['groups'] \
    if str(data[group].dshape[-1]) == '?datetime' or \
    is_date(bz.into(pd.Series, data[group].head(1000)))]

    typ['keywords'] = [group for group in typ['groups'] \
    if str(data[group].dshape[-1]) == '?string' and \
    has_keywords(bz.into(pd.Series, data[group].head(1000)))]

    return typ


def missing_percent(data):
    '''returns the percentage of missing values in the column

    parameters:
    ------------
        data: string

    usage:
    -------
        >>> count_missing_per(data['Species'])
        >>> 0 
    '''

    count = count_missing(data)
    size = data.size
    percentage = (100*count) / size
    return percentage

def strip_non_alphanum(text):
    ''' Return ```List``` of alphanumeric string by stripping the non
    alpha numeric characters
    Parameters
    ----------
    text : str
        unclean string with combination of alphanumeric and non alphanumeric

    Returns
    -------
    list : list of all alpha numeric strings
    Examples
    --------
        >>> strip_non_alphanum('epqenw49021[4;;ds..,.,uo]mfLCP'X')
        >>> ['epqenw49021', '4', 'ds', 'uo', 'mfLCP', 'X']
    '''
    return re.compile(r'\W+', re.UNICODE).split(text)



def word_freq_count(words):
    '''Return ``` dict``` which consist of each words as key and its frequency count as value
    Parameters
    ------------
    words: str

    Returns
    --------
    dict : dict of all words and its frequency count

    Examples:
        >>> word_freq_count("hello how are you")
        >>> {'a': 1, ' ': 3, 'e': 2, 'h': 2, 'l': 2, 'o': 3, 'r': 1,
        ... 'u': 1, 'w': 1, 'y': 1}
    '''
    return dict(zip(words, [words.count(p) for p in words]))


def ignore_stopwords(list_of_words):
    ''' Return list of words ignoring stopwords in the given list of words
    Parameters
    -----------
    list_of_words :  list
        length string is split into list of words using split function

    Examples:
        >>> ignore_stopwords("I am basically a lazy person and i hate computers")
        >>> ['I', 'basically', 'lazy', 'person', 'hate', 'computers']
    '''
    return [w for w in list_of_words if w not in stopwords]


def ignore_outlier(dataframe_numeric):
    ''' Return dataframe by removing outlier rows from given dataframe_numeric
    Parameters:
    -----------
    dataframe_numeric: pandas.dataframe
        Pandas dataframe consist of only numeric values

    Example:
    --------
        >>> df = pd.DataFrame(np.array([
                    [1,1,0],
                    [2,10,50000],
                    [1,14,10],
                    [3,100,11],
                    [10,1400,11],
                    [50,10,13],
                    [100,11,14],
                    [101,91,18],
                    [111,16,19],
                    [300,13,1],
                    [1000,1,1],
            ]))
        >>> ignore_outlier(df)
        >>> 0    1   2
        ... 0    1    1   0
        ... 2    1   14  10
        ... 3    3  100  11
        ... 5   50   10  13
        ... 6  100   11  14
        ... 7  101   91  18
        ... 8  111   16  19
        ... 9  300   13   1

    '''
    return dataframe_numeric[(np.abs(stats.zscore(dataframe_numeric)) < 3).all(axis=1)]


__all__ = [
    'geocode',
    'unique_value_count',
    'unique_identifier',
    'word_freq_count',
    'ignore_stopwords',
    'strip_non_alphanum',
    'date_split',
    'is_categorical',
    'count_missing',
    'is_date',
    'dict_query_string',
    'groupmeans',
    'ignore_outlier',
    'types',
    'encode',
    'describe',
    'missing_percent',
    'has_keywords'
]
