# -*- coding:utf8 -*-
'''
测试注册用户
'''

import config

import requests

import tornado
import tornado.web
import tornado.escape
import unittest

from torcms.model.user_model import MUser


class SimpleWidgetTestCase(unittest.TestCase):
    current_user = 'user'

    @tornado.web.authenticated
    def setUp(self):
        self.payload = {
            'user_name': 'xnamex',
            'user_pass': '131322',
        }

        self.uu = MUser()
        self.username = self.payload['user_name']

        post_data = {
            'user_name': self.payload['user_name'],
            'user_pass': self.payload['user_pass'],
            'user_email': 'name@kljhqq.com',
        }

        self.uu.insert_data(post_data)

        post_data = {
            'role': '3330'
        }
        tt = self.uu.update_role(self.username, post_data['role'])

        self.payload3 = {
            'uid': 'abcd',
            # 'title': '',
            'tags': 'JILU',
            'keywords': 'JILU',
            'logo': 'JILU',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',
            'def_cat_uid': '0301',
        }
        self.payload4 = {
            'uid': 'abcd',
            'title': 'DANWEI',
            # 'tags': 'JILU',
            'keywords': 'JILU',
            'logo': 'JILU',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',
            'def_cat_uid': '0301',
        }
        self.payload5 = {
            'uid': '1111',
            'title': '1111',
            'tags': '1111',
            'keywords': '111',
            'logo': '1111',
            'cnt_md': '111',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',
            'def_cat_uid': '0301',
        }
        self.payload6 = {
            'uid': '1111',
            #   'title': '1111',
            #  'tags': '1111',
            # 'keywords': '111',
            #  'logo': '1111',
            #  'cnt_md': '111',
            #  'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',
            'def_cat_uid': '0301',
        }
        self.payload7 = {
            'uid': '1111',
            'title': '1111',
            'tags': '1111',
            'keywords': '111',
            'logo': '1111',
            'cnt_md': '111',
            #  'ext_baidumap': '123',
            # 'ext_contributor': '123',
            # 'ext_contact_who': '123',
            'def_cat_uid': '0301',
        }

        # self.r = requests.post('{0}/user/login'.format(config.site_url), self.payload)

        # 记录登陆状态
        # self.s = requests.session()
        #
        # self.r1 = self.s.post('{0}/user/login'.format(config.site_url), self.payload)
        #
        # self.r2 = self.s.post('{0}/meta/cat_add/0301'.format(config.site_url), self.payload2)
        #
        # self.r3 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload2)
        #
        # self.payload2['def_cat_uid'] = '0301'
        #
        # self.r4 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload2)
        #
        # self.r5 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload3)
        #
        # self.r6 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload4)
        #
        # self.r7 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload5)
        #
        # self.r8 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload6)
        #
        # self.r9 = self.s.post('{0}/meta/to_add'.format(config.site_url), self.payload7)

    def tearDown(self):
        self.uu.delete_by_user_name(self.username)
        # self.muser.delete_by_user('value1')

    def testit(self):
        s = requests.session()
        r1 = s.post('{0}/user/login'.format(config.site_url), self.payload)
        assert r1.status_code == 200

    def test_22(self):
        # 记录登陆状态
        payload2 = {
            'uid': 'abcd',
            'title': 'DANWEI',
            'tags': 'JILU',
            'keywords': 'JILU',
            'logo': 'JILU',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',
            # 'def_cat_uid': '0301',
        }
        s = requests.session()
        s.post('{0}/user/login'.format(config.site_url), self.payload)

        r2 = s.post('{0}/meta/cat_add/0301'.format(config.site_url), self.data_post_add())

        assert r2.status_code == 500

    def data_post_add(self):
        payload2 = {
            'uid': 'abcd',
            'title': 'DANWEI',
            'tags': 'JILU',
            'keywords': 'JILU',
            'logo': 'JILU',
            'cnt_md': '123',
            'ext_baidumap': '123',
            'ext_contributor': '123',
            'ext_contact_who': '123',
            # 'def_cat_uid': '0301',
        }
        return payload2

    def test_33(self):
        # 记录登陆状态

        s = requests.session()
        s.post('{0}/user/login'.format(config.site_url), self.payload)

        r3 = s.post('{0}/post/_add'.format(config.site_url), self.data_post_add())

        assert r3.status_code == 200
        # Todo
        # assert self.r4.status_code == 200
        #
        # assert self.r5.status_code == 200
        # assert self.r6.status_code == 200
        # assert self.r7.status_code == 200
        # assert self.r8.status_code == 200
        # assert self.r9.status_code == 200
