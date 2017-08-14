# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
from django.conf import settings as django_settings
import re
try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse
from .oauthcore import get_verify_key, verifySign, set_parameters, getSign, get_sign_key
import logging
from django.http.response import HttpResponse
log_settings = "oauthlib"
if hasattr(django_settings, 'DJDG_AUTH'):
    log_settings = django_settings.DJDG_AUTH.get('log', log_settings)
log = logging.getLogger(log_settings)
from .oauthcore import to_unicode


class Http401Response(HttpResponse):

    status_code = 401


class OAuthClient(object):

    keys = dict()
    apps = dict()

    """
    TODO: add docs
    """

    def __init__(self):
        """
        :params server: An instance of oauthlib.oauth2.Server class
        """
        pass

    def _get_escaped_full_path(self, request):
        """
        Django considers "safe" some characters that aren't so for oauthlib.
        We have to search for them and properly escape.
        """
        parsed = list(urlparse(request.get_full_path()))
        return urlunparse(parsed)

    def _get_key_obj(self, appid):
        if self.keys.get(appid):
            keys_obj = self.keys.get(appid)
        else:
            keys_obj = get_verify_key(appid)
            self.keys[appid] = keys_obj
        return keys_obj

    def _get_app_obj(self, app):
        if self.apps.get(app):
            return self.apps[app]
        else:
            key_app = get_sign_key(app)
            self.apps[app] = key_app
            return key_app


    def _extract_params(self, request):
        """
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.method
        headers = self.extract_headers(request)
        body = self.extract_body(request)
        return uri, http_method, body, headers

    def extract_headers(self, request):
        """
        Extracts headers from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: a dictionary with OAuthLib needed headers
        """
        headers = request.META.copy()
        if 'HTTP_AUTHORIZATION' in headers:
            headers['Authorization'] = headers['HTTP_AUTHORIZATION']
        return headers

    def extract_body(self, request):
        """
        Extracts the POST body from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: provided POST parameters
        """
        CONTENT_TYPE = request.environ.get("CONTENT_TYPE")
        if CONTENT_TYPE and CONTENT_TYPE.upper().find("APPLICATION/JSON") >= 0:
            return request.body
        elif request.method == "GET":
            return request.GET.dict()
        else:
            return request.POST.dict()

    def verify_request(self, request):
        """
        :param request: The current django.http.HttpRequest object
        """
        if hasattr(django_settings, "DJDG_AUTH"):
            full_escape_url = django_settings.DJDG_AUTH.get(
                'FULL_ESCAPE_URL', [])
            regex_escape_url = django_settings.DJDG_AUTH.get(
                'REGEX_ESCAPE_URL', [])
            regex_check_url = django_settings.DJDG_AUTH.get(
                'REGEX_CHECK_URL', [])
            path = request.path.strip('/')
            if regex_check_url:
                for url in regex_check_url:
                    if re.match(url, path):
                        break
                else:
                    return
            else:
                if path in full_escape_url:
                    return
                for url in regex_escape_url:
                    if re.match(url, path):
                        return
        uri, http_method, body, headers = self._extract_params(request)
        dict_body = body
        if body and not isinstance(body, dict):
            dict_body = json.loads(body)
        if not dict_body.get("appid"):
            raise Exception(u"can not find appid in request body")
        appid = dict_body["appid"]
        keys_obj = self._get_key_obj(appid)
        if not keys_obj:
            raise Exception(
                "can not fetch any settings, please make sure appid incorrect")
        signature = headers.get("Authorization")
        request.client_type = keys_obj.app
        return verifySign(body, keys_obj.secret, signature)

    @staticmethod
    def oauth_request(url, method, app, parameters=None, headers=None, files=None):
        appkeys = OAuthClient()._get_app_obj(app)
        secret, parameters = set_parameters(parameters, appkeys)
        if method == "get":
            params = parameters
        else:
            params = json.dumps(to_unicode(parameters))
        try:
            signature = getSign(params, secret)
        except Exception as e:
            log.info(e.message)
            return {"statusCode": 500, "msg": e.message}
        headers_dict = {
            "Accept": "application/json",
            "Authorization": signature
        }
        if files:
            re = requests.Request(
                method=method, url=url,
                params=params, headers=headers_dict,
                files=files
                )
        elif method == "get":
            re = requests.Request(
                method=method, url=url,
                params=params, headers=headers_dict)
        else:
            headers_dict["Content-Type"] = "application/json; charset=utf-8"
            re = requests.Request(
                method=method, url=url,
                data=params, headers=headers_dict)
        pre_re = re.prepare()
        res_session = requests.Session()
        r = res_session.send(pre_re)
        if r.status_code != 200:
            log.error(r.content)
            return {"statusCode": 500, "msg": r.content}
        else:
                try:
                    log.info(r.json())
                    return {"statusCode": 0, "content": r.json()}
                except:
                    log.info(r.content)
                    return {"statusCode": 0, "content": r.content}
