#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-21 06:04:30
# Author: xujif
# -----
# Last Modified: 2017-08-16 02:01:34
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###

from .order import Order
from .tick import Tick
from .bar import Bar
from .types import *
import abc
from datetime import datetime


class RejectByCounterException(Exception):
    def __init__(self, reason):
        Exception.__init__(reason)


class Position:
    def __eq__(self, other):
        return other is not None and self.symbol == other.symbol and self.volume == other.volume

    def __init__(self, symbol, volume, price=0):
        self._symbol = symbol
        self._volume = volume
        self._price = float(price)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

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


class PositionBook:
    '''
        持仓记录单
    '''

    def __str__(self):
        return "份额：%d (冻结:%d,锁定:%d),现价:%.2f, 均价:%.2f,市值:%.2f,成本:%.2f" % (self._volume,self._frozen_volume,self._blocked_volume,self.price,self.avg_cost_price,self.market_value,self._cost)

    def __init__(self, symbol):
        self._exchange = ''
        self._symbol = symbol
        self._volume = 0
        self._price = 0
        self._frozen_volume = 0
        self._blocked_volume = 0
        self._cost = 0
        self._avg_cost_price = 0
        self._positions = list()

    def add_position(self, volume, price, blocked=False,update_market_price = False):
        p = Position(self._symbol, volume, price)
        self._positions.append(p)
        # 记录总量
        self._volume += volume
        # 总成本
        self._cost += volume * price
        # 平均成本
        self._avg_cost_price = self._cost / self._volume
        # 是否锁定
        if blocked:
            self._blocked_volume += volume
        if update_market_price:
            self._price = price

    @property
    def symbol(self):
        return self._symbol

    @property
    def volume(self):
        return self._volume

    @property
    def frozen_volume(self):
        '''
         冻结股份
        '''
        return self._frozen_volume

    def freeze_volume(self, volume):
        '''
         冻结指定数量的股份，卖出操作
        '''
        if self.free_volume < volume:
            return False
        self._frozen_volume += volume
        return True

    def cost_volume(self, volume):
        '''
        从冻结扣减股份，卖出成交操作
        '''

        if self._frozen_volume < volume:
            return False
        self._volume -= volume
        self._frozen_volume -= volume
        return True

    def release_volume(self, volume):
        '''
        释放冻结的股份
        '''
        if self._frozen_volume < volume:
            return False
        self._frozen_volume -= volume
        return True

    @property
    def cost(self):
        '''
        持有成本
        '''
        return self._cost

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value
        # 更新市值

    @property
    def avg_cost_price(self):
        '''
        平均成本
        '''
        return self._avg_cost_price

    @property
    def market_value(self):
        '''
         市值
        '''
        return self._price * self._volume

    @property
    def free_volume(self):
        '''
            可操作的股份
        '''
        return self._volume - self._frozen_volume - self._blocked_volume


class Account:

    def __str__(self):
        _str = "余额: %.2f, 冻结: %.2f 持仓: " % (
            self._balance, self._frozen_balance)
        if len(self.positions) == 0:
            _str += 'none'
        _str += ' 全部股票市值：%.2f' % self.market_value
        _str += ' 股票+现金：%.2f' % self.all
        return _str

    def __eq__(self, other):
        # 余额等全部相等
        if not (other is not None and self.all == other.all and self.balance == other.balance and self.frozen_balance == other.frozen_balance):
            return False
        else:
            for symbol in self._positionBookDic:
                if symbol not in other._positionBookDic:
                    return False
                elif other._positionBookDic[symbol] != self._positionBookDic[symbol]:
                    return False
            return True
        return True

    def __init__(self, balance, frozen_balance=0, positions=None):
        self._balance = float(balance)
        self._positionBookDic = {}
        self._frozen_balance = float(frozen_balance)
        # self._positions = positions if positions is not None else []


    @property
    def frozen_balance(self):
        return self._frozen_balance

    def freeze_balance(self, money):
        if money > self._balance:
            return False
        self._balance -= money
        self._frozen_balance += money
        return True

    def release_frozen_balance(self, money):
        '''
        释放冻结金额
        '''
        if money > self._frozen_balance:
            return False
        self._balance += money
        self._frozen_balance -= money
        return True

    def freeze_volume(self, symbol, volume):
        '''
        冻结股票份额，会从最早的可交易份额开始冻结
        '''
        if symbol not in self._positionBookDic:
            return False
        return self._positionBookDic[symbol].freeze_volume(volume)

    def cost_volume(self, symbol, volume):
        '''
        真实扣减股票份额
        '''
        if symbol not in self._positionBookDic:
            return False
        return self._positionBookDic[symbol].cost_volume(volume)

    def release_volume(self, symbol, volume):
        '''
        释放冻结的股份
        '''
        if symbol not in self._positionBookDic:
            return False
        return self._positionBookDic[symbol].release_volume(volume)

    

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
        if symbol not in self._positionBookDic:
            self._positionBookDic[symbol] = PositionBook(symbol)
        return self._positionBookDic[symbol].add_position(volume,price)

    @property
    def balance(self):
        return self._balance

    @property
    def positions(self):
        return self._positionBookDic.values()

    def get_positions(self):
        return self.positions

    def get_position(self,symbol):
        return self._positionBookDic[symbol] if symbol in self._positionBookDic else None

    def update_market_price(self, symbol, price):
        if symbol not in self._positionBookDic:
            return
        self._positionBookDic[symbol].price = price

    @property
    def market_value(self):
        '''
            股票总市值，不包含现金
        '''
        return sum(map(lambda p: p.market_value, self.positions))

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
        return sum(map(lambda p: p.cost, self.positions))

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
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].volume

    def get_frozen_volume_of_symbol(self, symbol):
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].frozen_volume

    def get_free_volume_of_symbol(self, symbol):
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].free_volume

class Counter:

    @abc.abstractclassmethod
    def query_account_sync(self):
        pass

    @abc.abstractclassmethod
    def mk_order_sync(self, order: Order):
        pass

    @abc.abstractclassmethod
    def query_order_sync(self, order_cid):
        pass

    @abc.abstractclassmethod
    def calcel_order(self, order_cid):
        pass

    def handle_bar(self, bar: Bar):
        pass

    def handle_tick(self, tick: Tick):
        pass


class BackTestCounter(Counter):

    @staticmethod
    def gen_ex_id():
        return datetime.now().strftime('ex%Y%m%d%H%M%S') + str(random.randrange(1000000, 9999999))

    def __init__(self, account: Account, bid_fee_radio=0, ask_fee_radio=0, transection_radio=1):
        Counter.__init__(self)
        self._account = account
        self._bid_fee_radio = bid_fee_radio
        self._ask_fee_radio = ask_fee_radio
        self.transection_radio = transection_radio
        self._orders = []
        self._last_error = None
        self._order_change_callback = None
        self._price_map = {}

    @property
    def assets(self):
        return self._account

    def set_order_cahnge_callback(self, callback):
        self._order_change_callback = callback

    def get_last_error(self):
        return self._last_error

    def register_order(self, order):
        order.ex_id = BackTestCounter.gen_ex_id()
        self._orders.append(order)

    def calcel_order(self, order_cid):
        for i in range(len(self._orders)):
            order = self._orders[i]
            if order.cid == order_cid:
                self.orders.pop(i)
                if order.status in [OrderStatus.CONFIRMED, OrderStatus.ORDER_PENDING]:
                    # 未产生交易，可直接取消
                    if order.order_side == OrderSide.BID:
                        # 买入释放冻结资金
                        self._account.release_frozen_balance(
                            order.frozen_money)
                        order.frozen_money = 0
                    else:
                        # 卖出释放股票份额
                        self._account.release_volume(
                            order.symbol, order.frozen_volume)
                        order.frozen_volume = 0
                    self.change_order_status(order, OrderStatus.CANCELED)
                elif order.status == OrderStatus.PART_FILLED:
                    self.change_order_status(order, OrderStatus.PART_CANCELED)
                break
        return True

    @property
    def orders(self):
        return self._orders

    @property
    def allow_to_open_short(self):
        return self.allow_to_open_short

    def query_account_sync(self)->Account:
        return self._account

    def mk_order_sync(self, order: Order):
        # q = self.get_quotation(order.symbol)
        if order.order_type == OrderType.LIMIT:
            if order.price == 0:
                self._last_error = '限价委托必须输入价格'
                return False
            # elif order.price > q.upper_limit or order.price < q.lower_limit:
            #     self._last_error = '价格超出范围'
            #     return False

        if order.order_side == OrderSide.BID:
            if order.order_type == OrderType.LIMIT:
                need_money = order.price * order.volume *\
                    (1 + self._bid_fee_radio)
            else:
                self._last_error = '回测只支持限价委托'
                return False
                # need_money = order.volume * q.upper_limit *\
                #     (1 + self._bid_fee_radio)
            if self._account.balance < need_money:
                self._last_error = '用户资金不足'
                return False
            if self.assets.freeze_balance(need_money):
                # 金额冻结成功
                order.frozen_money = need_money
                self.register_order(order)
                self.change_order_status(order, OrderStatus.CONFIRMED)
            else:
                self._last_error = '锁定资金失败'
                return False
        elif order.order_side == OrderSide.ASK:
            if self.assets.freeze_volume(order.symbol, order.volume):
                order.frozen_volume = order.volume
                self.register_order(order)
                self.change_order_status(order, OrderStatus.CONFIRMED)
            else:
                self._last_error = '可交易份额不足'
                return False

        return order

    def query_order_sync(self, order_cid):
        pass

    def change_order_status(self, order: Order, dst_status: OrderStatus):
        src_status = order.status
        order.status = dst_status
        # 触发订单事件
        if self._order_change_callback is not None:
            self._order_change_callback(order, src_status)

    def try_trade(self, symbol, price):
        for o in self._orders:
            if symbol != o.symbol:
                continue
            if o.status != OrderStatus.CONFIRMED and o.status != OrderStatus.PART_FILLED:
                continue
            if o.order_side == OrderSide.BID and price <= o.price:
                if o.order_type == OrderType.LIMIT:
                    successed_volume = o.volume * self.transection_radio
                    exchange_money = successed_volume * price
                    need_money = exchange_money * (1 + self._bid_fee_radio)
                    if self.assets.cost_frozen_balance(need_money):
                        o.filled_volume += successed_volume
                        o.filled_amount += exchange_money
                        o.frozen_money -= exchange_money
                        self._account.add_position(
                            o.symbol, successed_volume, price)
                        if self.transection_radio == 1:
                            self.change_order_status(o, OrderStatus.ALL_FILLED)
                        else:
                            # 订单完结，释放所有冻结金额
                            self.assets.release_frozen_balance(o.frozen_money)
                            o.frozen_money = 0
                            self.change_order_status(
                                o, OrderStatus.PART_FILLED)
                            # 剩余成交失败
                            self.change_order_status(
                                o, OrderStatus.PART_CANCELED)
                    else:
                        raise Exception('扣款失败，异常订单')

                elif o.order_type == OrderType.B5TC:
                    raise Exception('未实现')
                else:
                    print(o.order_type)
                    raise Exception('未实现')
            elif o.order_side == OrderSide.ASK and price >= o.price:
                if o.order_type == OrderType.LIMIT:
                    successed_volume = o.volume * self.transection_radio
                    exchange_money = successed_volume * price
                    return_money = exchange_money * (1 - self._bid_fee_radio)
                    if not self.assets.cost_volume(o.symbol, successed_volume):
                        raise Exception('股份扣减失败，异常订单')
                    o.filled_volume += successed_volume
                    o.filled_amount += return_money
                    o.frozen_volume -= successed_volume
                    self._account.add_balance(return_money)
                    if self.transection_radio == 1:
                        self.change_order_status(o, OrderStatus.ALL_FILLED)
                    else:
                        self.assets.release_volume(o.symbol, o.frozen_volume)
                        o.frozen_volume = 0
                        self.change_order_status(o, OrderStatus.PART_FILLED)
                        # 剩余成交失败
                        self.change_order_status(o, OrderStatus.PART_CANCELED)
                elif o.order_type == OrderType.B5TC:
                    raise Exception('未实现')
                else:
                    raise Exception('未实现')

    def handle_bar(self, bar: Bar):
        self._price_map[bar.symbol] = bar.close
        self.try_trade(bar.symbol, bar.close)
        self._account.update_market_price(bar.symbol, bar.close)

    def handle_tick(self, tick: Tick):
        self._price_map[tick.symbol] = tick.price
        self.try_trade(tick.symbol, tick.price)
        self._account.update_market_price(tick.symbol, tick.price)

    def handle_market_event(self, e: MarketEvent):
        if e.status == MarketStatus.PH:
            for o in self._orders:
                self.calcel_order(o)
