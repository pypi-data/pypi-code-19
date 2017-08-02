#!/usr/bin/env python
# encoding: utf-8

import os
import unittest
from datetime import timedelta

from zijin.zijin_data import get_market_data
from zijin.zijin_config import START_DATE, END_DATE
from zijin.zijin_functions import Strategy
from zijin.zijin_basic import strategy_run


class TestCase(unittest.TestCase):
    # def test1(self):
    #     get_market_data(START_DATE, END_DATE)
    #
    # def test2(self):
    #     strategy = Strategy(None, None, None)
    #     strategy.get_market_data(END_DATE - timedelta(days=1))

    def test3(self):
        predict_format = [
            {'name': '预测操作', 'type': 'string', 'information': '预测走势'},
            {'name': '正确率', 'type': 'float', 'information': '统计预测准确率'}
        ]

        strategy_run('/home/xxh/workspace/zijin/test', 'predict.py', 'predict', predict_format)

if __name__ == '__main__':
    unittest.main()