#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from auth import Token

r1 = Token.redirect('c2', 'https://auth.hypers.com.cn/oauth2/test/code')
print('1. Token.redirect(client_id, redirect_uri): /authorize接口uri拼接用于重定向:\n'+r1)
