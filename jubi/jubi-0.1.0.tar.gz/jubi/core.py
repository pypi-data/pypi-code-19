# -*- coding: utf-8 -*-
from enum import Enum
from hashlib import md5, sha256
import hmac
from typing import Dict
from urllib.parse import urlencode

from jubi.abc import Requester, Response
from jubi.utils import format_url, get_nonce


class URL(Enum):
    GET_BALANCE = 'https://www.jubi.com/api/v1/balance/'
    LIST_TRADES = 'https://www.jubi.com/api/v1/trade_list/'
    GET_TRADE = 'https://www.jubi.com/api/v1/trade_view/'
    CANCEL_TRADE = 'https://www.jubi.com/api/v1/trade_cancel/'
    ADD_TRADE = 'https://www.jubi.com/api/v1/trade_add/'


class Client:
    CONTENT_TYPE = 'application/x-www-form-urlencoded'
    USER_AGENT = 'python-jubi'

    def __init__(self, requester: Requester, public_key: str, private_key: str
                 ):
        self.requester = requester
        self._public_key = public_key.encode('utf-8')
        self._private_key = private_key.encode('utf-8')
        self._hmac_key = self._cal_hmac_key()

    async def get_balance(self, *, api_url=URL.GET_BALANCE.value) -> Response:
        """

        参数
        key - API key
        signature - signature
        nonce - nonce
        返回JSON dictionary
        asset - 折合人民币总余额
        cny_balance - 人民币总余额
        ltc_balance - 比特币总余额
        cny_lock - 人民币冻结余额
        ltc_lock - 比特币冻结余额
        ............
        nameauth - 实名认证状态 0 未实名 1 等待确认 2 已经认证成功
        moflag - 手机绑定状态 0 未绑定 1 绑定
        返回结果示例：
        {"uid":8,"nameauth":0,"moflag":0,"doge_balance":4234234,"doge_lock":0,"ltc_balance":32429.6,"ltc_lock":2.4,"xpm_balance":0,"xpm_lock":0,"cny_balance":2344581.519,"cny_lock":868862.481}
        """
        return await self.post(api_url, {}, data={})

    async def list_trades(self, coin: str, *, since: int = 0,
                          t_type: str = 'all',
                          api_url: str = URL.LIST_TRADES.value) -> Response:
        """您指定时间后的挂单，可以根据类型查询，比如查看正在挂单和全部挂单


        参数
        key - API key
        signature - signature
        nonce - nonce
        since - unix timestamp(utc timezone) default == 0, i.e. 返回所有
        coin - 币种简称,例如btc、ltc、xas
        type - 挂单类型[open:正在挂单, all:所有挂单]
        返回JSON dictionary
        id - 挂单ID
        datetime - date and time
        type - "buy" or "sell"
        price - price
        amount_original - 下单时数量
        amount_outstanding - 当前剩余数量
        返回结果示例：

            [{"id":"11","datetime":"2014-10-21 10:47:20","type":"sell",
             "price":42000,"amount_original":1.2,"amount_outstanding":1.2
             }, ...]
        """
        data = {
            'since': since,
            'coin': coin,
            'type': t_type,
        }
        return await self.post(api_url, {}, data=data)

    async def get_trade(self, id: str, coin: str, *,
                        api_url: str = URL.GET_TRADE.value) -> Response:
        """查询订单信息

        参数
        key - API key
        signature - signature
        nonce - nonce
        id - 挂单ID
        coin - 币种简称,例如btc、ltc、xas

        返回JSON dictionary

        id - 挂单ID
        datetime - 挂单时间（格式：YYYY-mm-dd HH:ii:ss）
        type - "buy" or "sell"
        price - 挂单价
        amount_original - 下单时数量
        amount_outstanding - 当前剩余数量
        status - 状态：new(新挂单), open(开放交易), cancelled(撤消), closed(完全成交)
        avg_price - 成交均价

        返回结果示例：

            {"id":11,"datetime":"2014-10-21 10:47:20","type":"sell",
             "price":42000,"amount_original":1.2,"amount_outstanding":1.2,
             "status":"closed"}
        """
        data = {
            'id': id,
            'coin': coin,
        }
        return await self.post(api_url, {}, data=data)

    async def cancel_trade(self, id: str, coin: str, *,
                           api_url: str = URL.CANCEL_TRADE.value) -> Response:
        """取消订单

        参数
        key - API key
        signature - signature
        nonce - nonce
        id - 挂单ID
        coin - 币种简称,例如btc、ltc、xas
        返回JSON dictionary
        result - true(成功), false(失败)
        id - 订单ID
        返回结果示例：
        {"result":true, "id":"11"}
        """
        data = {
            'id': id,
            'coin': coin,
        }
        return await self.post(api_url, {}, data=data)

    async def add_trade(self, coin: str, price: float, amount: float,
                        type: str, *, api_url: str = URL.ADD_TRADE.value
                        ) -> Response:
        """

        参数
        key - API key
        signature - signature
        nonce - nonce
        amount - 购买数量
        price - 购买价格
        type - 买单或者卖单(buy/sell)
        coin - 币种简称,例如btc、ltc、xas
        返回JSON dictionary
        id - 挂单ID
        result - true(成功), false(失败)
        返回结果示例：
        {"result":true, "id":"11"}
        """
        data = {
            'amount': amount,
            'price': price,
            'type': type,
            'coin': coin,
        }
        return await self.post(api_url, {}, data=data)

    async def get_ticker(self, coin) -> Response:
        """获取当前最新行情 - Ticker


        :param coin: 币种简称,例如btc、ltc、xas

        :return:


          返回JSON dictionary

            high - 最高价
            low - 最低价
            buy - 买一价
            sell - 卖一价
            last - 最近一次成交价
            vol - 成交量
            volume - 成交额

          返回结果示例：

            {"high":22,"low":20,"buy":1.879,"sell":0,
             "last":38800,"vol":283.954}
        """
        pass

    async def get_depth(coin) -> Response:
        """返回所有的市场深度，此回应的数据量会较大，所以请勿频繁调用。

        :param coin: 币种简称,例如btc、ltc、xas
        :return:

        返回JSON dictionary

          asks - 委买单[价格, 委单量]，价格从高到低排序
          bids - 委卖单[价格, 委单量]，价格从高到低排序

        返回结果示例：

          {"asks":[[70000,5],[69000,0.48], ... ]}
        """
        pass

    def list_orders(self, coin):
        """返回100个最近的市场交易，按时间倒序排列，此回应的数据量会较大，
        所以请勿频繁调用。


        参数
        coin - 币种简称,例如btc、ltc、xas
        返回JSON dictionary
        date - 时间戳
        price - 交易价格
        amount - 交易数量
        tid - 交易ID
        type - 交易类型
        返回结果示例：
        [{"date":"0","price":3,"amount":0.1,"tid":"1","type":"buy"},{"date":"0","price":32323,"amount":2,"tid":"2","type":"sell"},{"date":"0","price":32,"amount":432,"tid":"3","type":"sell"},{"date":"0","price":323,"amount":2,"tid":"4","type":"sell"},{"date":"0","price":2100,"amount":0.3,"tid":"5","type":"buy"}]
        """
        pass

    async def get_all_ticker(self) -> Response:
        """

        返回JSON dictionary
        high - 最高价
        low - 最低价
        buy - 买一价
        sell - 卖一价
        last - 最近一次成交价
        vol - 成交量
        volume - 成交额
        返回结果示例：
        {"ltc":{"high":217.68,"low":191.11,"buy":200.03,"sell":201.05,"last":200.03,"vol":34889,"volume":7147420},"btc":{"high":19540,"low":17000,"buy":17549.97,"sell":17549.98,"last":17549.97,"vol":366,"volume":6661461}}

        """
        pass

    async def _make_request(self, method: str, url: str, url_params: Dict,
                            data: Dict) -> Response:
        filled_url = format_url(url, url_params)
        request_headers = {
            'user_agent': self.USER_AGENT,
            'content-type': self.CONTENT_TYPE,
        }
        data.update({
            'nonce': get_nonce(),
            'key': self._public_key,
        })

        signature = self._cal_signature(data)
        data['signature'] = signature
        body = urlencode(data).encode('utf-8')

        response = await self.requester.request(
            method, filled_url, request_headers, body
        )
        return response

    async def get(self, url: str, url_params: Dict) -> Response:
        return await self._make_request('GET', url, url_params, {})

    async def post(self, url: str, url_params: Dict, *, data: Dict
                   ) -> Response:
        return await self._make_request('POST', url, url_params, data)

    async def put(self, url: str, url_params: Dict, *, data: Dict
                  ) -> Response:
        return await self._make_request('PUT', url, url_params, data)

    async def patch(self, url: str, url_params: Dict, *, data: Dict
                    ) -> Response:
        return await self._make_request('PATCH', url, url_params, data)

    async def delete(self, url: str, url_params: Dict) -> Response:
        return await self._make_request('DELETE', url, url_params, {})

    def _cal_hmac_key(self) -> bytes:
        key = md5(self._private_key).hexdigest()
        return key.encode('utf-8')

    def _cal_signature(self, params) -> str:
        message = urlencode(params).encode('utf-8')
        return hmac.new(self._hmac_key, message, digestmod=sha256).hexdigest()
