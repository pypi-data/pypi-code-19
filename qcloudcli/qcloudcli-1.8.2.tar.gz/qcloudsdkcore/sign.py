#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import hashlib
import hmac
import types

class Sign:
    def __init__(self, secretId, secretKey):
        self.secretId = secretId
        self.secretKey = secretKey

    def make(self, requestHost, requestUri, params, method = 'GET'):
        list = {}
        for param_key in params:
            if method == 'post' and str(params[param_key])[0:1] == "@":
                continue
            if(type(params[param_key]) == type([1,1])):
                for i in range(0, len(params[param_key])):
                    list[param_key+'.'+str(i) ] = params[param_key][i]
            else:
                list[param_key] = params[param_key]
        srcStr = method.upper() + requestHost + requestUri + '?' + "&".join(k.replace("_",".") + "=" + str(list[k]) for k in sorted(list.keys()))
        hashed = hmac.new(self.secretKey, srcStr, hashlib.sha1)
        return binascii.b2a_base64(hashed.digest())[:-1]

def main():
    secretId = 123
    secretKey = 'xxx'
    params = {}
    sign = Sign(secretId, secretKey)
    print sign.make('https://cvm.api.qcloud.com', '/v2/index.php', params)

if (__name__ == '__main__'):
    main()
