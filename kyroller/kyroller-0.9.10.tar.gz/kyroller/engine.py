#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-20 07:57:00
# Author: xujif
# -----
# Last Modified: 2017-08-16 04:11:56
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###
from abc import abstractmethod
from .strategy import Strategy
from .recivers import SocketIOReciver, AsyncRollbackReciver
from .types import *
from dateutil import parser
from time import mktime
from .apis import Api
import datetime as dt
import traceback


class Engine:
    def __init__(self, server, token, strategy):
        self.orders = dict()
        self.strategy = strategy
        self.api = Api('http://data-api.kuaiyutech.com/rpc2')
        self.counter = None
        self.subs = []
        self.timestamp = 0
        self.timestamp_end = 0
        self.shutdown_actions = []
        self.running = False

    def wait(self):
        while True:
            time.sleep(0.1)

    def plot_assets(self, interval=60):
        '''
        待实现
        '''
        pass
        # from .monitors import PlogMonitor
        # m = PlogMonitor()
        # self.strategy.add_monitor(m)
        # m.start()

    def sync_datas(self):
        '''
        同步数据到管理器
        '''
        pass

    def init(self, subs, counter, start_time=None, end_time=None):
        self.counter = counter
        self.subs = subs
        if start_time is not None:
            self.timestamp = start_time
        else:
            self.timestamp = time.time()
        if end_time is not None:
            self.timestamp_end = end_time
        else:
            self.timestamp_end = time.time() + 3600 * 7

        # 初始化策略
        self.strategy.print('initing', 'yellow')
        self.strategy.counter = counter
        self.strategy.api = self.api
        self.strategy.init(
            subs=subs,
            start_time=start_time,
            end_time=end_time)
        self.strategy.print('inited.', 'yellow')

    def handle_bar(self, bar: bar):
        pass

    def run_rollback(self, account, subs, start, end):
        '''
            回测模式运行
        '''
        start_time = mktime(parser.parse(start).timetuple()) + 9 * 3600 + 1800
        end_time = mktime(parser.parse(end).timetuple()) + 15 * 3600

        # 初始化策略
        counter = BackTestCounter(account)
        counter.set_order_cahnge_callback(
            self.strategy.handle_order_status_cahnge)
        self.init(
            subs,
            counter=counter,
            start_time=start_time,
            end_time=end_time)
        reciver = AsyncRollbackReciver(
            'http://rk.kuaiyutech.com', subs, start, end)
        self.running = True
        try:
            for (_type, msg) in reciver.generate_events():
                self.timestamp = msg.timestamp
                if _type == 'tick' or _type == 'quotation':
                    counter.handle_tick(msg)
                    self.strategy.handle_tick(msg)
                elif _type == 'bar':
                    counter.handle_bar(msg)
                    self.strategy.handle_bar(msg)
                elif _type == 'market':
                    self.strategy.handle_market_event(msg)
                    self.counter.handle_market_event(msg)
            print('end')
        except Exception as e:
            traceback.print_exc()
            print('运行出错:', e)
        self.running = False

    def run_as_worker(self):
        '''
            注册在线策略，可由管理器控制运行，推荐完成度较高的策略以此方式运行
        '''
        raise Exception('pending developing')
        pass

    def run_realtime(self, subs='tick_30s.sz000002', real_trade=False, assets=None):
        '''
            实盘运行
            @param real_trade 是否实盘交易，默认不开启
        '''
        # 初始化相关策略
        counter = BackTestCounter(assets)
        self.running = True
        try:
            reciver = SocketIOReciver('http://rt.kuaiyutech.com:12121', subs)
            self.init(
                subs,
                counter=counter)
            for (_type, msg) in reciver.generate_events():
                self.timestamp = msg.timestamp
                if _type == 'tick' or _type == 'quotation':
                    counter.handle_tick(msg)
                    self.strategy.handle_tick(msg)
                elif _type == 'bar':
                    counter.handle_bar(msg)
                    self.strategy.handle_bar(msg)
                elif _type == 'market':
                    self.strategy.handle_market_event(msg)
                    self.counter.handle_market_event(msg)
        except Exception as e:
            traceback.print_exc()
            print('运行出错:', e)

        self.running = False
