# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from six.moves.urllib import parse
from utility import post, APIError

__version__ = '0.0.1'
__author__ = 'Zhu Changjian (daya0576@gmail.com)'


BASE_URL = 'https://auth.hypers.com.cn/oauth2'


class Token(object):
    def __init__(self, access_token='', token_type='', refresh_token='', expiration=''):
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.expiration = expiration

    @staticmethod
    def redirect(client_id, redirect_uri, response_type='code'):
        """fetch redirect url

        BASE URL: https://auth.hypers.com.cn/oauth2/authorize
        Input:
            client_id
            redirect_uri
            response_type: code
        Output:
            (Redirect URL)
        """
        paras = dict(
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_type=response_type
        )
        url = "{}/authorize?{}".format(BASE_URL, parse.urlencode(paras))
        return url

    @classmethod
    def get(cls, client_id, client_secret, redirect_uri, code, grant_type='authorization_code'):
        """fetch token

        POST: https://auth.hypers.com.cn/oauth2/token
        Request:
            header: Content-Type: application/x-www-form-urlencoded
            body:
                client_id
                client_secret
                redirect_uri
                grant_type: authorization_code
                code
        Response:
            access_token, token_type, refresh_token, expiration
        """
        url = '{}/token'.format(BASE_URL)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = dict(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            code=code,
            grant_type=grant_type
        )

        result = post(url, parse.urlencode(data), headers)
        return cls(**result)

    def update(self, result):
        if 'error' in result:
            raise APIError(result['error'], result.get('error_description'))

        self.access_token = result.get('access_token', '')
        self.token_type = result.get('token_type', '')
        self.refresh_token = result.get('refresh_token', '')
        self.expiration = result.get('expiration', '')

        if not (self.access_token and self.token_type and self.refresh_token and self.expiration):
            raise APIError('token', '')

        return self

    def refresh(self, client_id, client_secret, grant_type='refresh_token'):
        """refresh token

        POST: https://auth.hypers.com.cn/oauth2/token
        Request:
            body:
                grant_type:refresh_token
                client_id
                client_secret
                refresh_token
        Response:
            access_token, token_type, refresh_token, expiration
        """
        url = '{}/token'.format(BASE_URL)
        data = dict(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=self.refresh_token,
            grant_type=grant_type
        )
        result = post(url, data, {})
        return self.update(result)

    def __str__(self):
        return '<Class: {}>\n' \
               'access_token:     "{}"\ntoken_type:       "{}"\n' \
               'refresh_token:    "{}"\nexpiration:       "{}"'.format(
                self.__class__.__name__,
                self.access_token, self.token_type, self.refresh_token, self.expiration)

    __repr__ = __str__
