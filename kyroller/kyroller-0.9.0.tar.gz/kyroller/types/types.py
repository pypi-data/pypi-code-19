#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-14 12:06:52
# Author: xujif
# -----
# Last Modified: 2017-08-15 12:59:34
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###
from abc import abstractmethod
from enum import Enum, unique
import time
import random
from functools import reduce
from datetime import datetime


class State(dict):
    def __getattribute__(self, name):
        if name not in self:
            return None
        else:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class IncorrectDataException(Exception):
    pass


@unique
class Exchange(Enum):
    SH = 0
    SZ = 1


@unique
class MarketStatus(Enum):
    '''
        PQ 开盘前
        KJ 开盘竞价
        PZ 盘中
        WX 午休
        CJ 收盘集合竞价
        PH 盘后
        ND 新的一天，回测中会用到
    '''
    PQ = 0
    KJ = 5
    PZ = 10
    WX = 15
    CJ = 20
    PH = 25
    ND = 1000


class MarketEvent:
    def __str__(self):
        return 'exchange: %s, timestamp: %s,_status: %s' % (self.exchange, datetime.fromtimestamp(self.timestamp), self._status.name)

    def __init__(self, exchange, timestamp, market_status):
        self._exchange = exchange
        self._timestamp = timestamp
        self._status = MarketStatus[market_status]

    @property
    def exchange(self)->Exchange:
        return self._exchange

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def status(self)->MarketStatus:
        return self._status


class Position:

    def __eq__(self, other):
        return other is not None and self.symbol == other.symbol and self.volume == other.volume

    def __init__(self, symbol, volume, price=0, frozen_volume=0, cost=None):
        self._symbol = symbol
        self._volume = volume
        self._price = float(price)
        self._cost = cost if cost is not None else self._price * self._volume
        self._cost_price = 0 if volume == 0 else self._cost / volume
        self._frozen_volume = frozen_volume

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def cost_price(self):
        return self._cost_price

    @property
    def market_value(self):
        return self._price * self._volume

    @property
    def free_volume(self):
        return self._volume - self._frozen_volume

    @property
    def frozen_volume(self):
        '''
         冻结股份
        '''
        return self._frozen_volume

    def freeze_volume(self, volume):
        if self.free_volume == 0:
            return 0
        elif self.free_volume < volume:
            # 不足，剩余的全部锁定
            v = self.free_volume
        else:
            v = volume
        self._frozen_volume += v
        return v

    def cost_volume(self, volume):
        '''
        扣减股份，返回 真实扣除股份
        '''
        if self._frozen_volume == 0:
            return 0
        elif self._frozen_volume < volume:
            # 不足，扣完
            dec = self._frozen_volume
        else:
            dec = volume
        self._volume -= dec
        self._frozen_volume -= dec
        return dec

    def release_volume(self, volume):
        '''
        释放冻结的股份
        '''
        if self._frozen_volume == 0:
            return 0
        elif self._frozen_volume < volume:
            v = self._frozen_volume
        else:
            v = volume
        self._frozen_volume -= v
        return v

    @property
    def cost(self):
        '''
        持有成本
        '''
        return self._cost

    @property
    def exchange(self)->Exchange:
        if self._symbol[0:2] == 'sh':
            return Exchange.SH
        elif self._symbol[0:2] == 'sz':
            return Exchange.SZ

    @property
    def symbol(self):
        return self._symbol

    @property
    def volume(self):
        return self._volume


class Account:

    def __str__(self):
        _str = "余额: %.2f, 冻结: %.2f 持仓: " % (
            self._balance, self._frozen_balance)
        if len(self._positions) == 0:
            _str += 'none'
        else:
            merged = self.merged_positions
            arr = map(lambda p: '%s=%d' %
                      (p.symbol, p.volume), merged)
            costs = map(lambda p: p.cost, merged)
            sum_of_values = reduce(lambda a, b: a + b, costs)
            sum_of_frozen = sum(map(lambda p: p.frozen_volume, merged))

            _str += ', '.join(arr)
            _str += '( cost: %d ,frozen: %d)' % (sum_of_values, sum_of_frozen)
        _str += ' 全部股票市值：%.2f' % self.market_value
        _str += ' 股票+现金：%.2f' % self.all
        return _str

    def __eq__(self, other):
        # 余额等全部相等
        if not (other is not None and self.all == other.all and self.balance == other.balance and self.frozen_balance == other.frozen_balance):
            return False
        else:
            a = self.merged_positions
            b = self.merged_positions
            if len(a) != len(b):
                return False
            for i in range(0, len(a)):
                if a[i] != b[i]:
                    return False
        return True

    def __init__(self, balance, frozen_balance=0, positions=None):
        self._balance = float(balance)
        self._frozen_balance = float(frozen_balance)
        self._positions = positions if positions is not None else []

    @property
    def frozen_balance(self):
        return self._frozen_balance

    def freeze_balance(self, money):
        if money > self._balance:
            return False
        self._balance -= money
        self._frozen_balance += money
        return True

    def freeze_volume(self, symbol, volume):
        '''
        冻结股票份额，会从最早的可交易份额开始冻结
        '''
        if self.get_free_volume_of_symbol(symbol) < volume:
            return False
        for p in self._positions:
            if volume == 0:
                break
            volume -= p.freeze_volume(volume)
        return True

    def cost_volume(self, symbol, volume):
        '''
        真实扣减股票份额
        '''
        if self.get_frozen_volume_of_symbol(symbol) < volume:
            return False
        for p in self._positions:
            if volume == 0:
                break
            volume -= p.cost_volume(volume)
        return True

    def release_volume(self, symbol, volume):
        '''
        释放冻结的股份
        '''
        if self.get_frozen_volume_of_symbol(symbol) < volume:
            return False
        for p in self._positions:
            if volume == 0:
                break
            volume -= p.release_volume(volume)
        return True

    def release_frozen_balance(self, money):
        if money > self._frozen_balance:
            return False
        self._balance += money
        self._frozen_balance -= money
        return True

    def add_balance(self, money):
        self._balance += money

    def cost_frozen_balance(self, money):
        if money > self._frozen_balance:
            return False
        self._frozen_balance -= money
        return True

    def add_position(self, symbol, volume, price):
        '''
         允许卖空
        '''
        p = Position(symbol=symbol, volume=volume, price=price)
        self._positions.append(p)

    @property
    def balance(self):
        return self._balance

    @property
    def positions(self):
        return self._positions

    def update_market_price(self, symbol, price):
        for p in self._positions:
            if p.symbol == symbol:
                p.price = price

    @property
    def market_value(self):
        '''
            股票总市值，不包含现金
        '''
        return sum(map(lambda p: p.market_value, self._positions))

    @property
    def cash(self):
        return self._balance + self._frozen_balance

    @property
    def all(self):
        '''
            股票总市值，包含现金
        '''
        return self.market_value + self._balance + self._frozen_balance

    @property
    def all_cost(self):
        '''
        股票总成本
        '''
        return sum(map(lambda p: p.cost, self._positions))

    def make_snapshot(self):
        return State({
            "balance": self._balance,
            "frozen_balance": self._frozen_balance,
            "cash": self.cash,
            "all_cost": self.all_cost,
            "market_value": self.market_value,
            "all": self.all
        })

    def get_volume_of_symbol(self, symbol):
        return sum(
            map(lambda p: p.volume, filter(
                lambda p: p.symbol == symbol, self._positions))
        )

    def get_frozen_volume_of_symbol(self, symbol):
        return sum(
            map(lambda p: p.frozen_volume, filter(
                lambda p: p.symbol == symbol, self._positions))
        )

    def get_free_volume_of_symbol(self, symbol):
        return sum(
            map(lambda p: p.free_volume, filter(
                lambda p: p.symbol == symbol, self._positions))
        )

    @property
    def merged_positions(self):
        dic = {}
        for p in self._positions:
            if p.symbol in dic:
                dic[p.symbol]['volume'] += p.volume
                dic[p.symbol]['cost'] += p.cost
                dic[p.symbol]['frozen_volume'] += p.frozen_volume
            else:
                dic[p.symbol] = {
                    'symbol': p.symbol,
                    'volume': p.volume,
                    'frozen_volume': p.frozen_volume,
                    'cost': p.cost,
                    'price': p.price
                }
        return list(map(lambda d: Position(d['symbol'], d['volume'], d['frozen_volume'], d['cost']), dic.values()))


class OrderSide(Enum):
    '''
    BID:买
    ASK:卖
    N:未标明（只在订单记录中出现，创建委托单请勿使用）
    '''
    N = 0
    BID = 1
    ASK = 2


class OrderType(Enum):
    '''
    委托单类型：
        LIMIT: 限价委托
        BOC : 对方最优价格(best of counterparty)
        BOP: 己方最优价格(best of party)
        B5TC: 最优五档剩余撤销(best 5 then cancel)
        B5TL: 最优五档剩余转限价(best 5 then limit)
        IOC: 即时成交剩余撤销(immediately or cancel)
        FOK: 即时全额成交或撤销(fill or kill)
        AON: 全额成交或不成交(all or none)
        MTL: 市价剩余转限价(market then limit)
    '''
    LIMIT = 0
    BOC = 1
    BOP = 2
    B5TC = 3
    B5TL = 4
    IOC = 5
    FOK = 6
    AON = 7
    MTL = 8


class OrderStatus(Enum):
    '''
    委托单状态：
        WAITING_TO_ORDER: 未报
        ORDER_PENDING: 报单中（已到达柜台或者券商，未发送到交易所）
        CONFIRMED: 已报单,待交易所处理
        PART_FILLED：部分成交
        ALL_FILLED：全部成交
        REJECTED：废单（风控系统拒绝）
        REJECTED_T：废单（券商或者交易所拒绝，余额不足或者价格错误等）
        CANCELED：已被撤单(全部撤单)
        PART_CANCELED : 已撤单（部分已成交）

    '''
    WAITING_TO_ORDER = 0
    ORDER_PENDING = 5
    CONFIRMED = 10
    PART_FILLED = 20
    ALL_FILLED = 25
    REJECTED = -10
    PART_CANCELED = -20
    CANCELED = -25
