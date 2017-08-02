#!/usr/bin/env python
# encoding: utf-8

from zijin_util import datetime2str

PREDICT_TYPE_MAP = {'int': int, 'float': float, 'string': str, 'bool': bool}


class Bar(object):
    """
    required attributes
    open: float
    high: float
    low: float
    close: float
    datetime: datetime
    trade_date: date
    volume: float
    """
    def __init__(self, **kargs):
        required_fields = ['open', 'high', 'low', 'close', 'datetime', 'trade_date', 'volume']
        for key in kargs:
            if key in required_fields:
                required_fields.remove(key)
        if len(required_fields) == 0:
            self.__dict__ = kargs
        else:
            raise Exception('fileds {:s} missing'.format(','.join(required_fields)))


class Order(object):
    """
    required attributes
    trade_date: date
    price: float
    trade_volume: float
    type: string
    datetime: datetime
    """
    def __init__(self, **kargs):
        required_fields = ['trade_date', 'price', 'volume', 'type', 'datetime']
        for key in kargs:
            if key in required_fields:
                required_fields.remove(key)
        if len(required_fields) == 0:
            self.__dict__ = kargs
        else:
            raise Exception('fields {:s} missing'.format(','.join(required_fields)))

    def __repr__(self):
        return ','.join([datetime2str(self.datetime), str(self.type), str(self.price), str(self.volume)])


class Predict(object):
    """
    required attributes
    datetime: datetime
    """
    def __init__(self, **kargs):
        required_fields = ['datetime']
        for key in kargs:
            if key in required_fields:
                required_fields.remove(key)
        if len(required_fields) == 0:
            self.__dict__ = kargs
        else:
            raise Exception('fields {:s} missing'.format(','.join(required_fields)))

    def is_valid(self, predict_format):
        for item in predict_format:
            value = getattr(self, item['name'], None)
            if value is None or not isinstance(value, PREDICT_TYPE_MAP[item['type']]):
                return False, 'predict data not match format: {:s} {:s}'.format(item['name'], item['type'])
            return True, ''



