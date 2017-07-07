#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
from auth import Token

code = (len(sys.argv) == 2 and sys.argv[-1]) or '1g8E16'
token = Token.get('c2', 's2', 'https://auth.hypers.com.cn/oauth2/test/code', code)
print('2.  get(cls, client_id, client_secret, redirect_uri, code) 用code换取token:\n'+str(token))
print()

token_new = token.refresh('c2', 's2')
print('3. self.refresh(用refresh token换取新token):\n'+str(token_new))
