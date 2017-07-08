# -*- coding:utf8 -*-
'''
测试注册用户
'''

import requests


import config
from torcms.model.usage_model import MUser

import unittest


class SimpleWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.payload = {'user_name': 'y',
                        'user_pass': 'y',
                        }
        self.payload2 = {'user_name': 'giser',
                        'user_pass': 'g131322',
                        }
        self.muser = MUser()
        self.r = requests.post('{0}/user/login'.format(config.site_url), self.payload)
        self.r2 = requests.post('{0}/user/login'.format(config.site_url), self.payload2)


class DefaultWidgetSizeTestCase2(SimpleWidgetTestCase):
    def Testit(self):
        print(self.r.status_code)

        assert self.r.status_code == 401
        assert self.r2.status_code == 200


    def test_dsf(self):
        print(self.r.status_code)

        assert self.r.status_code == 401
        assert self.r2.status_code == 200