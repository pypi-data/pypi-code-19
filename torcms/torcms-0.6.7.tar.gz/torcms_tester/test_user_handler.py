# -*- coding: utf-8

'''
测试注册用户
'''

import config

import requests

import tornado
import tornado.web
import tornado.escape
import unittest


class SimpleWidgetTestCase(unittest.TestCase):
    current_user = 'user'

    @tornado.web.authenticated
    def setUp(self):
        self.payload = {
            'user_name': 'giser',
            'user_pass': 'g131322',
        }

        self.payload2 = {
            'uid': 'abcd',
            'title': 'DANWEI',
            'tags': 'JILU',
            'keywords': 'JILU',
            'logo': 'JILU',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }
        self.payload3 = {
            'uid': 'abcd',
            'title': 'DANWEI',
            'tags': 'JILU',
            'keywords': 'JILU',
            'logo': 'JILU',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }
        self.payload4 = {
            'uid': 'abcd',
            'title': '1111',
            'tags': '111',
            'keywords': '111',
            'logo': '1111',

            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }
        self.payload5 = {
            'uid': 'abcd',
            # 'title': '1111',
            'tags': '111',
            'keywords': '111',
            'logo': '1111',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }
        self.payload6 = {
            'uid': 'abcd',
            'title': 'adsf',
            # 'tags': '111',
            'keywords': '111',
            'logo': '1111',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }
        self.payload7 = {
            'uid': 'abcd',
            'title': 'adsf',
            'tags': '111',
            # 'keywords': '111',
            'logo': '1111',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }
        self.payload8 = {
            'uid': 'abcd',
            'title': 'adsf',
            'tags': '111',
            'keywords': '111',
            # 'logo': '1111',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',

        }

        self.r = requests.post('{0}/user/login'.format(config.site_url), self.payload)

        # 记录登陆状态
        self.s = requests.session()

        self.r1 = self.s.post('{0}/user/login'.format(config.site_url), self.payload)

        self.r2 = self.s.post('{0}/meta/edit/6c9e'.format(config.site_url), self.payload2)

        self.r3 = self.s.post('{0}/meta/edit'.format(config.site_url), self.payload2)

        self.r4 = self.s.post('{0}/meta/edit/6c9e'.format(config.site_url), self.payload4)

        self.r5 = self.s.post('{0}/meta/edit/6c9e'.format(config.site_url), self.payload5)

        self.r6 = self.s.post('{0}/meta/edit/6c9e'.format(config.site_url), self.payload6)

        self.r7 = self.s.post('{0}/meta/edit/6c9e'.format(config.site_url), self.payload7)

        self.r8 = self.s.post('{0}/meta/edit/6c9e'.format(config.site_url), self.payload8)

    def tearDown(self):
        pass
        # self.muser.delete_by_user('value1')

    def testit(self):
        print(self.r1.status_code)
        print(self.r2.status_code)
        print(self.r3.status_code)

        assert self.r1.status_code == 200

        # Todo: 有问题
        # assert self.r2.status_code == 200
        #
        # assert self.r3.status_code == 500
        #
        # assert self.r4.status_code == 200
        #
        # assert self.r5.status_code == 500
        #
        # assert self.r6.status_code == 500
        #
        # assert self.r7.status_code == 500
        #
        # assert self.r8.status_code == 500
