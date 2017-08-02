import unittest
from datetime import timedelta

from zijin.zijin_data import get_market_data
from zijin.zijin_config import START_DATE, END_DATE
from zijin.zijin_functions import Strategy


class TestCase(unittest.TestCase):
    def test1(self):
        get_market_data(START_DATE, END_DATE)

    def test2(self):
        strategy = Strategy(None, None, None)
        print strategy.get_market_data(END_DATE - timedelta(days=1))

if __name__ == '__main__':
    unittest.main()