__author__ = 'Kevin'

import string
import datetime
from decimal import Decimal

_basedate = datetime.date(year=1900, month=1, day=1)
_basedatetime = datetime.datetime(year=1900, month=1, day=1)
_minuteseconds = Decimal(60.0)
_hourseconds = Decimal(3600.0)
_dayseconds = Decimal(86400.0)


def pos2address(row, col):
    """
    Calculates Excel Address-String from position
    :param row: Row Index (1 based)
    :type row: int
    :param col: Column Index (1 based)
    :type col: int
    :return: Address
    :rtype: str
    """
    abc = string.ascii_uppercase

    carryover = int((col-1)/len(abc))

    address = ""
    if carryover > 0:
        address += abc[carryover - 1]
        col -= carryover * len(abc)

    address += "{0}{1}".format(abc[col-1], row)

    return address

def reduce_dimensions(data, rows, cols):
    if rows == 1 and cols == 1:
        return data[0][0]
    elif rows == 1:
        return data[0]
    elif cols == 1:
        data1 = []
        for i in range(rows):
            data1.append(data[i][0])
        return data1
    else:
        return data
    #raise NotImplementedError()

def num2date(num):
    delta = datetime.timedelta(days=num - 2)
    return _basedate + delta

def date2num(date):
    delta = date - _basedate
    return delta.days + 2

def num2time(num):
    return (_basedatetime + datetime.timedelta(seconds=int(Decimal(num)*_dayseconds))).time()

def time2num(time):
    """

    :param time:
    :type time: datetime.time
    :return:
    """
    return (Decimal(time.hour)*_hourseconds + Decimal(time.minute)*_minuteseconds + Decimal(time.second))/_dayseconds

def datetime2num(dt):
    """

    :param dt:
    :type dt: datetime.datetime
    :return:
    """
    return time2num(dt.time()) + date2num(dt.date())

def num2datetime(num):
    days = int(num)
    secs = num - days
    return datetime.datetime.combine(num2date(days), num2time(secs))