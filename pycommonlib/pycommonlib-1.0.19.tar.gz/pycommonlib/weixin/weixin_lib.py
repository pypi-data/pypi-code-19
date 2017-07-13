# -*- coding: utf-8 -*-
import requests
import logging
import json
from django.conf import settings
from pycommonlib.util import cache
from .exceptions import APIError

CACHE_WEIXIN_ACCOUNTTOKEN = 'weixin_account_token'
CACHE_WEIXIN_ACCESSTOEKN = 'weixin_access_token_{}'
CACHE_WEIXIN_JS_TICKET = 'weixin_js_ticket'

_logger = logging.getLogger(__name__)


def get_token():
    token = cache.get(CACHE_WEIXIN_ACCOUNTTOKEN)
    if token:
        _logger.info('get_token load token from cache:{}'.format(token))
        return token
    # get token from weixin server
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
        settings.WEIXIN['app_id'], settings.WEIXIN['app_seckey'])
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        response_data = r.json()
        cache.put(CACHE_WEIXIN_ACCOUNTTOKEN, response_data['access_token'], response_data['expires_in'])
        _logger.info(_format_log_message('get_token succeed', r))
        return response_data['access_token']
    else:
        _logger.error(_format_log_message('get_token failed', r))
        raise APIError()


def get_access_token(code):
    '''
    @return: {'access_token':'','openid','','unionid':''}
    '''
    assert code
    cacheKey = CACHE_WEIXIN_ACCESSTOEKN.format(code)
    token = cache.get(cacheKey)
    if token:
        _logger.info('get_access_token load token from cache:{}'.format(token))
        return token
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code'.format(
        settings.WEIXIN['app_id'], settings.WEIXIN['app_seckey'], code)
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        response_data = r.json()
        if response_data.get('errcode', 0) == 0:
            _logger.info(_format_log_message('get_access_token succeed', r))
            token = {'access_token': response_data['access_token'],
                     'openid': response_data['openid'],
                     'unionid': response_data.get('unionid')}
            cache.put(cacheKey, token, response_data['expires_in'])
            return token
        else:
            _logger.error(_format_log_message('get_access_token failed', r))
            raise APIError()
    else:
        _logger.error(_format_log_message('get_access_token failed', r))
        raise APIError()


def refresh_access_toke(refreshToken):
    url = 'https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={}&grant_type=refresh_token&refresh_token={}'.format(
        settings.WEIXIN['app_id'], refreshToken)
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        response_data = r.json()
        if response_data.get('errcode', 0) == 0:
            _logger.info(_format_log_message('get_access_token succeed', r))
            return response_data
        else:
            _logger.error(_format_log_message('get_access_token failed', r))
            raise APIError()
    else:
        _logger.error(_format_log_message('get_access_token failed', r))
        raise APIError()


def get_jsapi_ticket():
    ticket = cache.get(CACHE_WEIXIN_JS_TICKET)
    if ticket:
        _logger.info('get_jsapi_ticket load ticket from cache:{}'.format(ticket))
        return ticket
    token = get_token()
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi'.format(token)
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        response_data = r.json()
        if response_data['errcode'] == 0:
            cache.put(CACHE_WEIXIN_JS_TICKET, response_data['ticket'], response_data['expires_in'])
            _logger.info(_format_log_message('get_jsapi_ticket succeed', r))
            return response_data['ticket']
        else:
            _logger.error(_format_log_message('get_jsapi_ticket failed', r))
            raise APIError()
    else:
        _logger.error(_format_log_message('get_jsapi_ticket failed', r))
        raise APIError()


def get_user_info(openId):
    token = get_token()
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN'.format(token, openId)
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        response_data = r.json()
        if 'errcode' in response_data:
            _logger.error(_format_log_message('get_user_info failed', r))
            raise APIError()
        else:
            _logger.info(_format_log_message('get_user_info succeed', r))
            return r.json()
    else:
        _logger.error(_format_log_message('get_user_info failed', r))
        raise APIError()


def sent_template_message(toOpenId, templateId, url, templateData):
    data = {"touser": toOpenId, "template_id": templateId, "url": url, "topcolor": "#FF0000", "data": templateData}
    token = get_token()
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(token)
    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
    if r.status_code == 200:
        response_data = r.json()
        if response_data['errcode'] == 0:
            _logger.info(_format_log_message('sent_template_message succeed', r))
        else:
            _logger.error(_format_log_message('sent_template_message failed', r))
            raise APIError()
    else:
        _logger.error(_format_log_message('sent_template_message failed', r))
        raise APIError()


def _format_log_message(message, r):
    return u'''
           {}
           url:{}
           response code:{}
           response body:{}
           '''.format(message, r.url, r.status_code, r.text)
