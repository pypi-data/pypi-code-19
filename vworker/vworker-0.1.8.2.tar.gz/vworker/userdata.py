#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Userdata(object):
    """ 用户信息
    """

    def update(self, data):
        """ 更新
        """
        self.__dict__.clear()
        self.__dict__.update(data)

    @property
    def login_status(self):
        """ 登录状态
        """
        if self.__dict__:
            return True
        return False

    def raise_for_status(self):
        """ 检查登录状态
        """
        if not self.login_status:
            raise ValueError(604, u'请重新登录')

    def roleis(self, role):
        """ 判断role
        """
        if self.login_status and str(getattr(self, 'role', None)) == str(role).lower():
            return True
        return False

usercard = Userdata()
