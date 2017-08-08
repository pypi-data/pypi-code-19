# -*- coding:utf-8 -*-
""" Created by FizLin on 2017/08/08/-下午10:15
    mail: https://github.com/Fiz1994
"""
from django.utils.deprecation import MiddlewareMixin
from page.models import ViewCount


class UpdateViewCountMiddleware(MiddlewareMixin):
    """ update view count"""

    # process_request
    def process_request(self, request):
        try:
            url = request.get_full_path()
            print(url)
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            res = ViewCount.objects.create(url=url, client_ip=ip)
            print('visit url :{0}, ip is {1}'.format(url, ip))
        except Exception:
            raise Exception
