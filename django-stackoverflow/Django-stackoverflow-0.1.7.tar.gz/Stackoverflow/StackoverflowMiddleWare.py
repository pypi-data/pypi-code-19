# -*- coding:utf-8 -*-
import requests
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
class ExceptionStackoverflowMiddleWare(MiddlewareMixin):
    """ process exception with stackoverflow"""

    def process_exception(self, request, exception):
        """
        处理异常 直接调用API 去查询这个异常
        :param request:
        :param exception:
        :return:
        """
        print('some thing is woring ,you can check with below link')
        intitle = u'{}'.format(exception.__class__.__name__)
        self.__get_answer(intitle)
        return None

    def __get_answer(self, exception_context):
        url = 'https://api.stackexchange.com/2.2/questions'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        params = {
            'order': 'desc',
            'sort': 'votes',
            'site': 'stackoverflow',
            # 'page': 3,
            # 'pagesize': 3,
            'filter': 'default',
            'tagged': 'python;django',
            'todate': datetime.now().strftime('%Y-%m-%d'),
            'intitle': exception_context
        }
        r = requests.get(url, params=params, headers=headers)
        questions = r.json()
        for question in questions['items']:
            print(question['title'])
            print(question['link'])
