#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import requests
import copy
import time
import random
import sys
import warnings
import os
warnings.filterwarnings("ignore")

from sign import Sign
from userInfo import UserInfo

class Request(UserInfo):
    timeout = 10
    version = 'qcloudcliV1'
    def __init__(self, product, version, action_name, requestHost):
        UserInfo.__init__(self, secret_id='123', secret_key='123', method='GET', region_id='gz', auto_retry=True, max_retry_time=3, user_agent=None, port=80)
        #self, secret_id = '123', secret_key = '123', method = 'GET', region_id = 'gz', auto_retry = True, max_retry_time = 3, user_agent = None, port = 80
        self.__requestHost = requestHost
        self.__requestUri = '/v2/index.php'
        self.__params = {}
        self.__product = product
        self.__version = version
        self.__action_name = action_name
        self.__debug = 0
        self.__files = {}

    def add_param(self, k, v):
        if self.__params is None:
           self.__params = {}
        self.__params[k] = v

    def get_params(self):
        return self.__params

    def set_product(self, product):
        self.__product = product

    def get_product(self):
        return self.__product

    def set_version(self, version):
        self.__version = version

    def get_version(self):
        return self.__version

    def set_action_name(self, action_name):
        self.__action_name = action_name

    def get_action_name(self):
        return self.__action_name

    def getUrl(self):
        self.checkParams(self.__action_name, self.__params)
        self.__params['RequestSource'] = self.__version
        sign = Sign(self.secret_id, self.secret_key)
        self.__params['Signature'] = sign.make(self.__requestHost, self.__requestUri, self.__params, self.request_method)
        params = urllib.urlencode(self.__params)

        url = 'https://%s%s' % (self.__requestHost, self.__requestUri)
        if (self.request_method.upper() == 'GET'):
            url += '?' + params
        return url

    def call(self):
        self.checkParams(self.__action_name, self.__params)
        self.__params['RequestSource'] = self.__version
        sign = Sign(self.secret_id, self.secret_key)
        self.__params['Signature'] = sign.make(self.__requestHost, self.__requestUri, self.__params, self.request_method)

        url = 'https://%s%s' % (self.__requestHost, self.__requestUri)

        if (self.request_method.upper() == 'GET'):
            req = requests.get(url, params=self.__params, timeout=self.timeout, verify=False)
            if (self.__debug):
                print 'url:', req.url, '\n'
        else:
            req = requests.post(url, data=self.__params, files=self.__files, timeout=self.timeout, verify=False)
            if (self.__debug):
                print 'url:', req.url, '\n'

        if req.status_code != requests.codes.ok:
            req.raise_for_status()

        return req.text

    def checkParams(self, action, params):
        for key in params.keys():
            if (type(params[key]) == type([1, 1])):
                if (type(params[key][0]) == type({'a':1,'b':2})):
                    for i in range(0, len(params[key])):
                        for k in params[key][i].keys():
                            if(type(params[key][i][k]) == type([1, 1])):
                                for m in range(0, len(params[key][i][k])):
                                    params[key + '.' + str(i)+'.'+ k + '.' + str(m)] =  params[key][i][k][m];
                            else:
                                params[key + '.' + str(i)+'.'+ k] = params[key][i][k]
                else:
                    for i in range(0, len(params[key])):
                        params[key + '.' + str(i)] = params[key][i]
                del params[key]
        self.__params = copy.deepcopy(params)
        self.__params['Action'] = action
        if (self.__params.has_key('Region') != True):
            self.__params['Region'] = self.region_id

        if (self.__params.has_key('SecretId') != True):
            self.__params['SecretId'] = self.secret_id

        if (self.__params.has_key('Nonce') != True):
            self.__params['Nonce'] = random.randint(1, sys.maxint)

        if (self.__params.has_key('Timestamp') != True):
            self.__params['Timestamp'] = int(time.time())

        return self.__params
