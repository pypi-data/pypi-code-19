# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-

import logging
import json

import requests
from requests.auth import HTTPBasicAuth

from nauth.clients.auth_client import AuthClient, AuthCheckTokenPayload

logger = logging.getLogger()


class UaaClient(AuthClient):
    def __init__(self, auth_client_config):
        AuthClient.__init__(self, auth_client_config)
        self._sign_key = None

    @property
    def id_token_endpoint(self):
        if self._id_token_endpoint is None:
            return self.get_url_for_endpoint("/oauth/token/")
        return self._id_token_endpoint

    @property
    def check_token_endpoint(self):
        if self._check_token_endpoint is None:
            return self.get_url_for_endpoint("/check_token")
        return self._check_token_endpoint

    @property
    def user_management_endpoint(self):
        return self.get_url_for_endpoint("/Users")

    @property
    def password_reset_code_endpoint(self):
        return self.get_url_for_endpoint("/password_resets")

    @property
    def password_reset_endpoint(self):
        return self.get_url_for_endpoint("/forgot_password")

    def get_sign_key(self):
        if self._sign_key is None:
            auth = self._get_auth()
            token_key_url = self.get_url_for_endpoint("/token_key")
            res = requests.get(token_key_url, auth=auth)
            payload = AuthClient.get_json_payload(res)
            self._sign_key = payload["value"]
        return self._sign_key

    def get_id_token_data_payload(self, data):
        data = super(UaaClient, self).set_id_token_data_payload(data)
        return data

    def _make_id_token_request(self, data):
        auth = self._get_auth()
        url = self.id_token_endpoint
        return requests.post(url, data=data, auth=auth)

    def _make_check_token_request(self, token):
        auth = self._get_auth()
        data = {"token": token}
        url = self.check_token_endpoint
        res = requests.post(url, data=data, auth=auth)
        return res

    def _get_access_token(self):
        auth = self._get_auth()
        url = self.id_token_endpoint
        params = {'grant_type': 'client_credentials', 'response_type': 'token'}
        res = requests.post(url, params=params, auth=auth)
        if res.status_code == 200:
            res = json.loads(res.text)
            return res["access_token"]

        return None

    def _get_auth(self):
        return HTTPBasicAuth(self._client_id, self._client_secret)

    def _get_auth_header(self):
        return {'Authorization': 'Bearer ' + self._get_access_token()}

    def get_check_token_response(self, token):
        res = self._make_check_token_request(token)

        if res.status_code == 200:
            res = AuthClient.get_json_payload(res)
            return AuthCheckTokenPayload(
                email=res["email"],
                tenant="Nervana Systems"
            )

        logger.error(res.text)
        logger.error("Unable to check token {}".format(token))

        return None

    def register_user(self, user, password, tenant=None):
        data = {
            "userName": user.email,
            "name": {
                "givenName": user.last_name,
                "familyName": user.last_name
            },
            "emails": [{"value": user.email, "primary": True}],
            "password": password,
        }

        res = requests.post(self.user_management_endpoint, json=data,
                            headers=self._get_auth_header())
        if res.status_code != 201:
            raise RuntimeError('User registration in UAA failed.'
                               ' Status code: {}, Response: {}'
                               .format(res.status_code, res.text))

    def _get_password_reset_code(self, user_id=None):
        data = user_id
        res = requests.post(self.password_reset_code_endpoint, data=data,
                            headers=self._get_auth_header())
        if res.status_code == 201:
            res = json.loads(res.text)
            return res["code"]
        else:
            logger.error('Failed to obtain UAA password reset code.'
                         ' Status code: {}, Response: {}'
                         .format(res.status_code, res.text))
            return None

    def get_password_reset_url(self, user_id=None, url=None):
        # Password reset URL points to the same endpoint for all UAA users
        code = self._get_password_reset_code(user_id)
        if code:
            return '{reset_url}?code={code}'.format(
                reset_url=self.password_reset_endpoint,
                code=code)
        else:
            return None

    def get_userid(self, email):
        """
        Checks if user with given email exists in UAA.
        Returns email back as an UAA userid.
        """
        user_id = None
        params = {'filter': 'email eq "{}"'.format(email)}
        res = requests.get(self.user_management_endpoint, params=params,
                           headers=self._get_auth_header())
        if res.status_code == 200:
            res = json.loads(res.text)
            if len(res["resources"]) > 0:
                user_id = email
        else:
            logger.error("Failed to obtain UAA's user id."
                         "Status code: {}, Response: {}"
                         .format(res.status_code, res.text))
        return user_id
