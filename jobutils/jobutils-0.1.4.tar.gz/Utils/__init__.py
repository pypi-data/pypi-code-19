#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
import time
from ast import literal_eval
from difflib import get_close_matches
from itertools import groupby
import functools
from dateutil import parser
import numpy as np
import random
import resource
import multiprocessing

from functools import reduce
from dateutil import parser
from pandas._libs.tslib import Timestamp

__author__ = "laurynas@joberate.com"


def decorator_f(function, *args, **kwargs):
    """
    Logs function run time
    :param function:
    :return:
    """
    @functools.wraps(function)
    def func_wrapper(*args, **kwargs):

        return function(*args, **kwargs)

    return func_wrapper


def memory_usage_decorator(function, *args, **kwargs):
    """
    Logs function memory usage
    :param function:
    :param args:
    :param kwargs:
    :return:
    """
    @functools.wraps(function)
    def func_wrapper(*args, **kwargs):

        print(function, ',', get_peak_memory_usage())
        function(*args, **kwargs)
        print(function, ',', get_peak_memory_usage())

    return func_wrapper


def runtime_decorator(function, *args, **kwargs):
    """

    :param function:
    :param args:
    :param kwargs:
    :return:
    """
    @functools.wraps(function)
    def func_wrapper(*args, **kwargs):

        start_timestamp = time.time()
        result = function(*args, **kwargs)
        end_timestamp = time.time()

        value = '%s,%s\n' % (function.__name__, end_timestamp - start_timestamp)
        print(value)
        return result

    return func_wrapper


def get_peak_memory_usage():
    """

    :return:
    """
    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


@decorator_f
def combine_time_data(date, time):
    """
    Combines time and date
    :param time:
    :param date:
    :return:
    """
    date_object = parse_date(str.join('-', [date.split('/')[2], date.split('/')[1], date.split('/')[0]]))
    time_object = parse_date(time)

    combined = datetime.datetime(date_object.year, date_object.month, date_object.day, time_object.hour, time_object.minute, time_object.second)

    return combined


@decorator_f
def convert_timestamp_to_datetime(timestamp):
    """

    :param timestamp:
    :return: datetime object in UTC format
    """
    return datetime.datetime.utcfromtimestamp(timestamp)


@decorator_f
def convert_time_to_int(time):
    """
    Converting time to microsecond timestamp
    :param time: time string in HH:MM:SS format
    :return: time in format
    """
    return time.microsecond + time.second * 1000 + time.minute * 60000 + time.hour + 3600000


@decorator_f
def extract_date_string(date_raw):
    """
    Converts datetime object to string representation
    :param date_raw:
    :return:
    """
    return str(date_raw.year) + str(date_raw.month) + str(date_raw.day)


@decorator_f
def extract_time(date):
    """

    :param date:
    :return:
    """
    return date.time()


@decorator_f
def get_closest_index(string, strings):
    """

    :param string:
    :param strings:
    :return:
    """
    closest_match = get_close_matches(string, strings)[0]
    return list(strings).index(closest_match)


@decorator_f
def generate_random_color(self):
    """
    Generates random hex color
    :return: str representing random hex color
    """
    return '#%02X%02X%02X' % (get_random_number(), get_random_number(), get_random_number())


@decorator_f
def get_random_number(max_value=255):
    """

    :return:
    """
    return random.randint(0, max_value)


@decorator_f
def get_consecutive_value_groups(data, step_size=0):
    """

    :param data:
    :param step_size:
    :return:
    """
    return np.split(data, np.where(np.diff(data) != step_size)[0]+1)


@decorator_f
def get_current_time(time_format=''):
    """

    :return:
    """
    time_value = datetime.datetime.now().time()
    if len(time_format) == 0:
        return time_value
    else:
        return time_value.strftime(time_format)


@decorator_f
def get_current_date(date_format=''):
    """

    :return:
    """
    date_value = datetime.datetime.now()
    if len(date_format) == 0:
        return date_value
    else:
        return date_value.strftime(date_format)


@decorator_f
def parse_date(date_string):
    """

    :param date_string:
    :return:
    """
    if type(date_string) == Timestamp:
        return date_string.to_pydatetime()

    return parser.parse(date_string)


@decorator_f
def time_in_range(start_time, end_time, context_time):
    """
    Returns true if x is in the range [start, end]
    :param start_time: Time object describing start time
    :param end_time: Time object describing end time
    :param context_time: Time object
    :return: True if context time is in between of start_time/end_time
    """
    if start_time <= end_time:
        return start_time <= context_time <= end_time
    else:
        return start_time <= context_time or context_time <= end_time


@decorator_f
def filter_value_from_dictionary(dictionary, key, argument=''):
    """

    :param dictionary:
    :param key:
    :param argument:
    :return:
    """
    result = filter(lambda address: key in address['types'], dictionary)
    if len(result) > 0:
        if len(argument) > 0:
            return result[0][argument]

    return ''


def try_get_value_from_dictionary(dictionary, keys, fallback_value=''):
    """

    :param dictionary:
    :param keys:
    :param fallback_value:
    :return:
    """
    for key in keys:
        if key in dictionary:
            value = dictionary[key]
            dictionary = dictionary[key]
            if type(value) is str:
                value = value.lower()
        else:
            return fallback_value

    if not value:
        return fallback_value

    return value


@decorator_f
def fix_date(dates_raw):
    """
    Parses raw date string to format YYYYMMDD
    :param dates_raw: list of ints representing date
    :return: list of date strings in format YYYYMMDD
    """
    dates = []
    for date_raw in dates_raw:
        date_raw = str(date_raw)
        year = date_raw[0:4]
        month = day = ''
        remainder = date_raw[4:len(date_raw)]
        if len(remainder) == 4:
            month = date_raw[4:6]
            day = date_raw[6:8]

        if len(remainder) == 2:
            month = '0' + date_raw[4:5]
            day = '0' + date_raw[5:6]

        if len(remainder) == 3:
            if int(date_raw[4:6]) > 12:
                month = '0' + date_raw[4:5]
                day = date_raw[5:7]
            else:
                month = date_raw[4:6]
                day = '0' + date_raw[6:]

        dates.append(year + month + day)

    return dates


@decorator_f
def get_processor_count():
    """
    returns logical processor count in machine
    :return:
    """
    return multiprocessing.cpu_count()


@decorator_f
def fix_time_date_component(component):
    """

    :param component:
    :return:
    """
    if component < 10:
        return '0%s' % component

    return component


@decorator_f
def remove_consecutive_duplicates(data):
    """

    :param data:
    :return:
    """
    return [x[0] for x in groupby(data)]


@decorator_f
def combine_date_time(raw_date):
    """

    :param raw_date:
    :return:
    """
    return "%s%s" % (str(raw_date.date()).replace('-', ''), str(raw_date.time()).replace(':', ''))


@decorator_f
def divide_nullable_values(a, b):
    """

    :param a:
    :param b:
    :return:
    """
    if a == 0 or b == 0:
        return 0

    return a/(b*1.0)


@decorator_f
def fix_nan_in_dictionary(dictionary):
    """

    :param dictionary:
    :return:
    """
    for key in dictionary:
        value = str(dictionary[key]).lower()
        if value == 'nan':
            dictionary[key] = 0

    return dictionary


@decorator_f
def apply_function_to_data(values, fun):
    """

    :param values:
    :param fun:
    :return:
    """
    return fun(values)


@decorator_f
def find_closest_multiplier(x, base=10):
    """

    :param x:
    :param base:
    :return:
    """
    return int(base * round(float(x) / base))


def merge_dictionaries(dicts):
    """

    :param dicts:
    :return:
    """
    result = {}
    for dictionary in dicts:
        for key in dictionary:
            result[key] = dictionary[key]

    return result


def convert_dictionary_to_string(dictionary):
    """
    Returns string representation of dictionary
    :param dictionary:
    :return:
    """
    values = []
    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            values.extend(convert_dictionary_to_string(dictionary[key]))
        else:
            values.append('%s-%s' % (key, dictionary[key]))

    return values


def generate_dictionary_hash(dictionary):
    """
    Generates hash of dictionary
    :param dictionary:
    :return:
    """
    dictionary_strings = convert_dictionary_to_string(dictionary)
    return str(hash('_'.join(dictionary_strings)))


def parse_date_string(text):
    """
    Parses string into date
    :param text: Text string representation
    :return:
    """
    return parser.parse(text)

def flatten_list_of_lists(l):
    """

    :param l:
    :return:
    """
    return reduce(lambda x, y: x + y, l)


def get_hash(string):
    """

    :param string:
    :return:
    """
    hash_object = hashlib.md5(string.encode())
    return hash_object.hexdigest()


def flatten_value(value):
    """

    :param value:
    :return:
    """
    if isinstance(value, list) and len(value) == 1:
        return flatten_value(value[0])
    else:
        return value


def decode_json(value):
    """
    Check if string is a valid JSON and, if positive, decode it
    :param value:
    :return: parsed new_value
    """
    value = unicode(value).strip().replace(': nan,', ': "",')
    try:
        return json.loads(value, encoding="utf-8")
    except ValueError:
        try:
            return literal_eval(value)
        except:
            return value

def convert_list_to_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for j in range(0, len(l), n):
        yield l[j:j + n]
