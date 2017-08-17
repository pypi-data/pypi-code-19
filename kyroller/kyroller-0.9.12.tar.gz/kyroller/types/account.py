from .position_book import Position, PositionBook
from .types import *


class Account:
    def __str__(self):
        _str = "余额: %.2f, 冻结: %.2f 持仓: " % (
            self._balance, self._frozen_balance)
        if len(self.positions) == 0:
            _str += 'none'
        else:
            arr = map(lambda p: '%s(volume:%d,cost:%.2f,market:%.2f)' %
                      (p.symbol, p.volume, p.cost, p.market_value), self.positions)
            _str += ', '.join(arr)
        _str += ' 全部股票市值：%.2f' % self.market_value
        _str += ' 股票+现金：%.2f' % self.all
        return _str

    def __eq__(self, other):
        # 余额等全部相等
        if other is None or self.balance != other.balance or self.frozen_balance != other.frozen_balance:
            return False
        else:
            pos1 = self._positionBookDic
            pos2 = other._positionBookDic
            if len(pos1) != len(pos2):
                return False
            for symbol in pos1:
                if symbol not in pos2:
                    return False
                elif pos1[symbol].volume != pos2[symbol].volume:
                    return False
            return True
        return True

    def __init__(self, balance, frozen_balance=0, positions=None):
        self._balance = float(balance)
        self._positionBookDic = {}
        self._frozen_balance = float(frozen_balance)
        if positions is not None:
            for p in positions:
                if p.symbol not in self._positionBookDic:
                    book = PositionBook(p.symbol)
                    self._positionBookDic[p.symbol] = book
                self._positionBookDic[p.symbol].add_position(
                    p.volume, p.price, update_market_price=True)

        self._orders = []

    @property
    def frozen_balance(self):
        '''
        冻结金额，买入下单后会冻结相关金额
        '''
        return self._frozen_balance

    def freeze_balance(self, money):
        '''
        冻结金额，内部api
        '''
        if money > self._balance:
            return False
        self._balance -= money
        self._frozen_balance += money
        return True

    def release_frozen_balance(self, money):
        '''
        释放冻结金额，内部api
        '''
        if money > self._frozen_balance:
            return False
        self._balance += money
        self._frozen_balance -= money
        return True

    def freeze_volume(self, symbol, volume):
        '''
        冻结股票份额，内部api
        '''
        if symbol not in self._positionBookDic:
            return False
        return self._positionBookDic[symbol].freeze_volume(volume)

    def cost_volume(self, symbol, volume):
        '''
        真实扣减股票份额，内部api
        '''
        if symbol not in self._positionBookDic:
            return False
        return self._positionBookDic[symbol].cost_volume(volume)

    def release_volume(self, symbol, volume):
        '''
        释放冻结的股份，内部api
        '''
        if symbol not in self._positionBookDic:
            return False
        return self._positionBookDic[symbol].release_volume(volume)

    def add_balance(self, money):
        '''
        增加余额，内部api
        '''
        self._balance += money

    def cost_frozen_balance(self, money):
        '''
        扣减冻结的金额，订单成交时会扣除冻结金额，内部api
        '''
        if money > self._frozen_balance:
            return False
        self._frozen_balance -= money
        return True

    def add_position(self, symbol, volume, price):
        '''
        增加份额，买入订单成交时调用，内部api
        '''
        if symbol not in self._positionBookDic:
            self._positionBookDic[symbol] = PositionBook(symbol)
        return self._positionBookDic[symbol].add_position(volume, price)

    @property
    def balance(self):
        '''
        可用余额
        '''
        return self._balance

    @property
    def positions(self):
        '''
        持仓列表
        '''
        return self._positionBookDic.values()

    def get_positions(self):
        '''
        返回持仓列表
        '''
        return self.positions

    def get_position(self, symbol):
        '''
        返回制定代码的持仓，如果为空，返回 None
        '''
        return self._positionBookDic[symbol] if symbol in self._positionBookDic else None

    def update_market_price(self, symbol, price):
        '''
        更新股票价格，更新市值,内部api
        '''
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
        '''
        现金，包含余额+冻结部分
        '''
        return self._balance + self._frozen_balance

    @property
    def total_value(self):
        '''
        总市值，包含现金
        '''
        return self.market_value + self._balance + self._frozen_balance

    @property
    def total_cost(self):
        '''
        股票总成本
        '''
        return sum(map(lambda p: p.cost, self.positions))

    def make_snapshot(self):
        '''
        创建资产快照，最好不要频繁调用
        '''
        return State({
            "balance": self._balance,
            "frozen_balance": self._frozen_balance,
            "cash": self.cash,
            "total_cost": self.total_cost,
            "market_value": self.market_value,
            "total_value": self.total_value
        })

    def get_volume_of_symbol(self, symbol):
        '''
        返回指定股票持有份额，包含所有状态
        '''
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].volume

    def get_frozen_volume_of_symbol(self, symbol):
        '''
        返回指定股票被冻结的份额，卖出中
        '''
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].frozen_volume

    def get_free_volume_of_symbol(self, symbol):
        '''
        返回指定股票可交易部分的份额
        '''
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].free_volume

    def get_locked_volume_of_symbol(self, symbol):
        '''
        返回指定股票锁定的份额
        '''
        if symbol not in self._positionBookDic:
            return 0
        return self._positionBookDic[symbol].locked_volume
