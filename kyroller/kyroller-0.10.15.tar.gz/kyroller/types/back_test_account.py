from .account import Account
from .position_book import Position, PositionBook
from .types import *
from .order import Order
import abc
from .tick import Tick
from .bar import Bar
from .exe_rpt import ExecutionRpt


class BackTestAccount(Account):

    def __init__(self, balance, frozen_balance=0, positions=None, bid_fee_radio=0, ask_fee_radio=0, transection_radio=1):
        Account.__init__(self, balance, frozen_balance,
                         positions, bid_fee_radio, ask_fee_radio)
        self._price_map = {}
        self._transection_radio = transection_radio

    @staticmethod
    def gen_ex_id():
        return datetime.now().strftime('ex%Y%m%d%H%M%S') + str(random.randrange(1000000, 9999999))

    def _change_order_status(self, order: Order, dst_status: OrderStatus):
        '''
        改变订单状态
        '''
        src_status = order.status
        order.status = dst_status
        # 触发订单事件
        if self._order_change_callback is not None:
            self._order_change_callback(order, src_status)

    def _register_order(self, order):
        order.ex_id = BackTestAccount.gen_ex_id()
        self._orders.append(order)

    def mk_order(self, order: Order):
        # q = self.get_quotation(order.symbol)
        if order.order_type == OrderType.LIMIT:
            if order.price == 0:
                raise TradeError('限价委托必须输入价格')
            # elif order.price > q.upper_limit or order.price < q.lower_limit:
            #     self._last_error = '价格超出范围'
            #     return False

        if order.order_side == OrderSide.BID:
            if order.order_type == OrderType.LIMIT:
                need_money = order.price * order.volume *\
                    (1 + self._bid_fee_radio)
            else:
                raise TradeError('回测只支持限价委托')
                # need_money = order.volume * q.upper_limit *\
                #     (1 + self._bid_fee_radio)
            if self.balance < need_money:
                raise TradeError('用户资金不足')

            if self.freeze_balance(need_money):
                # 金额冻结成功
                order.frozen_money = need_money
                self._register_order(order)
                self._change_order_status(order, OrderStatus.CONFIRMED)
                # 金额冻结成功
                order.frozen_money = need_money
                self._register_order(order)
                self._change_order_status(order, OrderStatus.CONFIRMED)
            else:
                raise TradeError('锁定资金失败')
        elif order.order_side == OrderSide.ASK:
            if self.freeze_volume(order.symbol, order.volume):
                order.frozen_volume = order.volume
                self._register_order(order)
                self._change_order_status(order, OrderStatus.CONFIRMED)
            else:
                raise TradeError('可交易份额不足')
        return order

    def cancel_order(self, order_cid):
        '''
        取消订单
        '''
        for i in range(len(self._orders)):
            order = self._orders[i]
            if order.cid == order_cid:
                self._orders.pop(i)
                if order.status in [OrderStatus.CONFIRMED, OrderStatus.ORDER_PENDING]:
                    # 未产生交易，可直接取消
                    if order.order_side == OrderSide.BID:
                        # 买入释放冻结资金
                        self.release_frozen_balance(
                            order.frozen_money)
                        order.frozen_money = 0
                    else:
                        # 卖出释放股票份额
                        self.release_volume(
                            order.symbol, order.frozen_volume)
                        order.frozen_volume = 0
                    self._change_order_status(order, OrderStatus.CANCELED)
                elif order.status == OrderStatus.PART_FILLED:
                    self._change_order_status(order, OrderStatus.PART_CANCELED)
                break
        return True

    def _try_trade(self, symbol, price, timestamp):
        '''
        尝试撮合
        '''
        for o in self._orders:
            if symbol != o.symbol:
                continue
            if o.status != OrderStatus.CONFIRMED and o.status != OrderStatus.PART_FILLED:
                continue
            if o.order_side == OrderSide.BID and price <= o.price:
                if o.order_type == OrderType.LIMIT:
                    successed_volume = o.volume * self._transection_radio
                    exchange_money = successed_volume * price
                    need_money = exchange_money * (1 + self._bid_fee_radio)
                    if self.cost_frozen_balance(need_money):
                        o.filled_volume += successed_volume
                        o.filled_amount += exchange_money
                        o.frozen_money -= exchange_money
                        self.add_position(
                            o.symbol, successed_volume, price)
                        rpt = ExecutionRpt(o.cid, o.symbol, o.side,
                                           o.volume, price, timestamp)
                        self._order_rpt(rpt)
                        if self._transection_radio == 1:
                            self._change_order_status(
                                o, OrderStatus.ALL_FILLED)
                        else:
                            # 订单完结，释放所有冻结金额
                            self.release_frozen_balance(o.frozen_money)
                            o.frozen_money = 0
                            self._change_order_status(
                                o, OrderStatus.PART_FILLED)
                            # 剩余成交失败
                            self._change_order_status(
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
                    successed_volume = o.volume * self._transection_radio
                    exchange_money = successed_volume * price
                    return_money = exchange_money * (1 - self._bid_fee_radio)
                    if not self.cost_volume(o.symbol, successed_volume, price):
                        raise Exception('股份扣减失败，异常订单')
                    o.filled_volume += successed_volume
                    o.filled_amount += return_money
                    o.frozen_volume -= successed_volume
                    self.add_balance(return_money)
                    rpt = ExecutionRpt(o.cid, o.symbol, o.side,
                                       o.volume, price, timestamp)
                    self._order_rpt(rpt)
                    if self._transection_radio == 1:
                        self._change_order_status(o, OrderStatus.ALL_FILLED)
                    else:
                        self.release_volume(o.symbol, o.frozen_volume)
                        o.frozen_volume = 0
                        self._change_order_status(o, OrderStatus.PART_FILLED)
                        # 剩余成交失败
                        self._change_order_status(o, OrderStatus.PART_CANCELED)
                elif o.order_type == OrderType.B5TC:
                    raise Exception('未实现')
                else:
                    raise Exception('未实现')

    def handle_bar(self, bar: Bar):
        self._price_map[bar.symbol] = bar.close
        self._try_trade(bar.symbol, bar.close, bar.timestamp)
        self.update_market_price(bar.symbol, bar.close)

    def handle_tick(self, tick: Tick):
        self._price_map[tick.symbol] = tick.price
        self._try_trade(tick.symbol, tick.price, tick.timestamp)
        self.update_market_price(tick.symbol, tick.price)

    def handle_market_event(self, e: MarketEvent):
        if e.status == MarketStatus.PH:
            for o in self._orders:
                self.cancel_order(o)

    def handle_events(self, _type, msg):
        if _type == 'tick' or _type == 'quotation':
            self.handle_tick(msg)
        elif _type == 'bar':
            self.handle_bar(msg)
        elif _type == 'market':
            self.handle_market_event(msg)
