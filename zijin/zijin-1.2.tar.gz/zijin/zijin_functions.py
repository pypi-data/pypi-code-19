#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime, timedelta, date
from bson.objectid import ObjectId
import os

from zijin_objects import Predict, Order
from zijin_util import error_decorator, date2str
from zijin_log import zijin_log, zijin_order, zijin_predict
from zijin_data import get_market_data
from zijin_config import LOG_PREFIX, LOG_DIR, ORDER_PREFIX, ORDER_DIR, LOG_SUFFIX, ORDER_SUFFIX, \
    PREDICT_DIR, PREDICT_PREFIX, PREDICT_SUFFIX


class SimpleResource(object):
    def __init__(self, id_=None):
        if id_ is None:
            self.id = ObjectId()
        else:
            self.id = id_


class Strategy(object):
    callback_function_names = ['on_init', 'on_start', 'on_stop', 'on_tick', 'on_bar', 'on_order', 'on_newday']
    provide_function_names = ['buy', 'sell', 'short', 'cover', 'log', 'predict', 'get_time', 'get_market_data']

    def __init__(self, user_script, script_mode, predict_format):
        context = SimpleResource()
        function = SimpleResource()
        var = SimpleResource()
        context.var = var
        context.function = function
        self._datetime = None
        self._trade_date = None
        self._context = context
        self._script = user_script
        self._script_mode = script_mode
        if self._script_mode == 'predict':
            self._predict_format = predict_format

        for name in self.callback_function_names:
            setattr(self, name, error_decorator(getattr(self, name)))
        for name in self.provide_function_names:
            setattr(function, name, getattr(self, name))

    def on_init(self):
        self._script.on_init(self._context)

    def on_start(self):
        self._script.on_start(self._context)

    def on_stop(self):
        self._script.on_stop(self._context)

    def on_bar(self, bar):
        self._context.var.bar = bar
        self._script.on_bar(self._context)

    def on_tick(self, tick):
        self._context.var.tick = tick
        self._script.on_tick(self._context)

    def on_order(self, order):
        print 'using on_order......'
        self._script.on_order(self._context)

    def on_newday(self):
        self._script.on_newday(self._context)

    def datetime_update(self, _datetime, trade_date):
        self._datetime = _datetime
        self._trade_date = trade_date

    def buy(self, price, volume=1):
        self.send_order('buy', price, volume)

    def sell(self, price, volume=1):
        self.send_order('sell', price, volume)

    def short(self, price, volume=1):
        self.send_order('sell', price, volume)

    def cover(self, price, volume=1):
        self.send_order('buy', price, volume)

    def send_order(self, type, price, volume):
        _datetime, trade_date = self.get_time()
        arg_dict = {'trade_date': trade_date, 'price': price, 'type': type, 'volume': volume,
                    'datetime': _datetime}
        order = Order(**arg_dict)
        zijin_order(os.path.join(ORDER_DIR, ORDER_PREFIX + date2str(trade_date) + ORDER_SUFFIX), order)

    def get_market_data(self, trade_date, type='bar'):
        if isinstance(trade_date, date):
            try:
                bars = get_market_data(start_date=trade_date, end_date=trade_date + timedelta(days=1))[trade_date]
            except KeyError:
                bars = []
        elif isinstance(trade_date, datetime):
            try:
                trade_date = datetime.date()
                bars =  get_market_data(start_date=trade_date, end_date=trade_date + timedelta(days=1))[trade_date]
            except KeyError:
                bars = []
        else:
            bars = []
        return [vars(bar) for bar in bars]

    def get_time(self):
        if self._datetime is None:
            now_datetime = datetime.now()
        else:
            now_datetime = self._datetime

        if self._trade_date is None:
            trade_date = self._datetime.date()
        else:
            trade_date = self._trade_date
        return now_datetime, trade_date

    def log(self, content):
        now_datetime, trade_date = self.get_time()
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        elif not isinstance(content, str):
            content = repr(content)
        zijin_log(os.path.join(LOG_DIR, LOG_PREFIX + date2str(trade_date) + LOG_SUFFIX), content + '\r\n')

    def predict(self, data):
        if self._script_mode != 'predict':
            raise Exception('use predict function in trade strategy')
        if not isinstance(data, dict):
            raise Exception('predict data must be dict')
        now_datetime, trade_date = self.get_time()
        data['datetime'] = now_datetime
        predict = Predict(**data)
        is_valid, error = predict.is_valid(self._predict_format)
        if not is_valid:
            raise Exception(error)
        zijin_predict(os.path.join(PREDICT_DIR, PREDICT_PREFIX + date2str(trade_date) + PREDICT_SUFFIX), vars(predict))


class StrategyManager(object):
    def __init__(self):
        super(StrategyManager, self).__init__()

    def run_strategy(self, script_path, script_mode, predict_format, start_date, end_date):
        script = None
        exec 'import {:s} as script'.format(script_path)
        strategy = Strategy(script, script_mode, predict_format)
        for function_name in strategy.callback_function_names:
            if not hasattr(script, function_name):
                raise Exception('{:s} function missing'.format(function_name))
        start = False
        first_day = True
        market_date = get_market_data(start_date=start_date, end_date=end_date)
        current_date = start_date
        print 'run strategy.....'
        strategy.on_init()
        while current_date < end_date:
            print 'date {:s} start'.format(date2str(current_date))
            try:
                bars = market_date[current_date]
            except KeyError:
                current_date = current_date + timedelta(days=1)
                continue
            strategy.datetime_update(datetime.combine(current_date, datetime.min.time()), current_date)
            if not start:
                strategy.on_start()
                start = True
            if first_day:
                first_day = False
            else:
                strategy.on_newday()
            for bar in bars:
                strategy.datetime_update(bar.datetime, current_date)
                strategy.on_bar(bar)
            current_date = current_date + timedelta(days=1)
            print 'date {:s} end'.format(date2str(current_date))