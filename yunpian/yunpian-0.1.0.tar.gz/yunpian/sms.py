# -*- coding: utf-8 -*-
from enum import Enum

from yunpian.core import Client
from yunpian.utils import clean_none


class URL(Enum):
    SINGLE_SEND = 'https://sms.yunpian.com/v2/sms/single_send.json'


class SMSClient(Client):
    """封装短信相关 API"""

    async def single_send(self, mobile: str, text: str, *,
                          extend: str = None, uid: str = None,
                          callback_url: str = None,
                          register: bool = None,
                          mobile_stat: bool = None,
                          api_url: str = URL.SINGLE_SEND.value):
        """单条发送接口

        https://www.yunpian.com/api2.0/api-domestic/single_send.html

        :param mobile:
        :param text:
        :param extend:
        :param uid:
        :param callback_url:
        :param register:
        :param mobile_stat:
        :param api_url:
        :return:
        """
        data = {
            'apikey': self._api_key,
            'mobile': mobile,
            'text': text,
            'extend': extend,
            'uid': uid,
            'callback_url': callback_url,
            'register': register,
            'mobile_stat': mobile_stat,
        }
        return await self.post(api_url, {}, data=clean_none(data))
