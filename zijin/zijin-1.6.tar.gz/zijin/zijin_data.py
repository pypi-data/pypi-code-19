#!/usr/bin/env python
# encoding: utf-8


from collections import defaultdict
from datetime import datetime
import csv
import inspect
import os

from zijin_objects import Bar


def line_to_bar(line_content):
    """
    change csv line content to object bar
    :param line_content: string 
    :return: 
    """
    cell_array = line_content
    trade_datetime = datetime.strptime(cell_array[1], '%Y-%m-%d %H:%M:%S.%f')
    trade_date = trade_datetime.date()
    open_price = float(cell_array[2])
    high_price = float(cell_array[3])
    low_price = float(cell_array[4])
    close_price = float(cell_array[5])
    volume = float(cell_array[6])
    kargs = {'open': open_price, 'high': high_price, 'low': low_price,
             'close': close_price, 'datetime': trade_datetime, 'volume': volume,
             'trade_date': trade_date}
    return Bar(**kargs)


# the data.csv is provided automatically
def get_market_data(start_date, end_date):
    print 'loading data .....'
    dir_name = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    path = os.path.join(dir_name, 'data.csv')
    market_data = defaultdict(list)
    with open(path, 'r') as csv_file:
        content = csv.reader(csv_file)
        next(content, None)
        for line in content:
            bar = line_to_bar(line)
            market_data[bar.trade_date].append(bar)
    return {k: v for k, v in market_data.iteritems() if start_date <= k < end_date}