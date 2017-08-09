"""
Written by: Ian Doarn

Basic utilities for 
use in other modules
"""
import json
import os
import re
from collections import OrderedDict
from zbsmsa.utils.exceptions import InvalidRange
from zbsmsa.utils.constants import *

PATH = os.path.dirname(os.path.realpath(__file__))


def __read_table(soup_obj, headers, table_class_id, table_index):
    tbl = soup_obj.find_all('table', {'class': table_class_id})[table_index]
    rows = []
    row_number = 1
    for tr in tbl.select('tr'):
        if tr.has_attr('class'):
            strings = [string for string in tr.stripped_strings]
            r = OrderedDict(zip(headers, strings))
            r['row'] = row_number
            row_number += 1
            rows.append(r)
    return rows


def read_table(soup_obj, table=None):
    readable_tables = ['stock', 'transfer']
    if type(table) is not str:
        raise ValueError('table arg must be a str')
    if table.lower() not in readable_tables:
        raise ValueError('{} not a supported table to read. Supported Tables: {}'.format(table, str(readable_tables)))
    if table.lower() == 'stock':
        return __read_table(soup_obj, STOCK_TABLE_HEADERS, STOCK_TABLE_CLASS_ID, STOCK_TABLE_CLASS_INDEX)
    elif table.lower() == 'transfer':
        return __read_table(soup_obj, TRANSFER_TABLE_HEADERS, TRANSFER_TABLE_CLASS_ID, TRANSFER_TABLE_CLASS_INDEX)


def concat_selectors(*args, concat=''):
    """
    Combines strings, since some selectors 
    paths and variable names when combines 
    are MUCH longer than 127 chars
    
    :param args: Variable amount of strings to combine
    :param concat: Char to concat with
    :return: combined string
    """
    return concat.join(args)


def load_selectors(file, path=os.path.join(PATH, 'json')):
    """
    Load css selector json file into python
    :param file: json file
    :param path: path to json files, default @ zbsmsa/utils/json
    :return: selectors
    """
    with open(os.path.join(path, file), 'r')as f:
        data = json.load(f)
    f.close()
    return data


def get_range_from_results(results, multi_page=False):
    """
    Get min and max range of table from results
    at the end of table
    
    When SMS tells you how many results there are, it
    usually looks like:
        
        1-25 of 25
        
    This uses regex to ensure the results are formatted this way
    it then split the text on the 'of' and again on the '-'
    We can then get the min and max range to use when iterating a table
    
    If the regex match returns false, we raise an error saying that
    the results passed in are invalid
    
    REGEX EXPLANATION
    ===========================================================
    (?:(?P<min>\d{1,4})-(?P<max>\d{1,4})\s(?P<of>of)\s(?P=max))
    ===========================================================
     - Non-capturing group (?:(?P<min>\d{1,4})-(?P<max>\d{1,4})\s(?P<of>of)\s(?P=max))
     - Named Capture Group min (?P<min>\d{1,4})
     - \d{1,4} matches a digit (equal to [0-9])
     - {1,4} Quantifier — Matches between 1 and 4 times, as many times as possible, giving back as needed (greedy)
     - - matches the character - literally (case sensitive)
     - Named Capture Group max (?P<max>\d{1,4})
     - \d{1,4} matches a digit (equal to [0-9])
     - {1,4} Quantifier — Matches between 1 and 4 times, as many times as possible, giving back as needed (greedy)
     - \s matches any whitespace character (equal to [\r\n\t\f\v ])
     - Named Capture Group of (?P<of>of)
     - of matches the characters of literally (case sensitive)
     - \s matches any whitespace character (equal to [\r\n\t\f\v ])
     - (?P=max) matches the same text as most recently matched by the capturing group named max
     - Global pattern flags
     - g modifier: global. All matches (don't return after first match)
    
    :param results: String from site
    :param multi_page: If table has multiple pages
    :return: min value, max value
    """
    # TODO: Figure out how to loop back when results are still loading or set a time out.
    # TODO: Some sort of case when results are 100+; either throw error or attempt to go to next page?
    # TODO: Add case when we are iterating multiple pages and format will be different

    # Regex pattern to match the format
    # #### - #### of ####
    pattern = re.compile(r"(?:(?P<min>\d{1,4})-(?P<max>\d{1,4})\s(?P<of>of)\s(?P=max))")

    if results == 'Loading...':
        raise InvalidRange(results, msg='Results still loading.')

    elif results == '1-1 of 1':
        return 1, 1

    elif results == 'No records':
        raise InvalidRange(results, msg='No records.')

    elif not multi_page:

        if results == '1-100 of 100+':
            raise InvalidRange(results, msg="Range to large.")

        if bool(pattern.match(results)):
            search_range = results.split('of')[0].split('-')
            return int(search_range[0].replace(' ', '')), int(search_range[1].replace(' ', ''))
        else:
            raise InvalidRange(results)

    elif multi_page:
        if bool(pattern.match(results)):
            search_range = results.replace('+', '').split('of')[0].split('-')
            search_range = [i.replace(' ', '') for i in search_range]

            x, y = search_range[0], search_range[1]

            if x == '1' and y == '100':
                return 1, 100
            elif x[-2:] == '01' and y[-2:] == '00':
                return 1, 100
            elif y[-2:] != '00':
                return 1, int(y[-2:])
        else:
            raise InvalidRange(results)
