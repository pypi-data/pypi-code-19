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

import json

import pytest

from nauth.tests.fixtures.requests import get, post  # noqa
from nauth.clients.auth_client import AuthClientConfig
from nauth.clients.uaa_client import UaaClient


class FakeRequest(object):
    def __init__(self, url="", data="", auth="", params="", headers="",
                 json=""):
            self.url = url
            self.data = data
            self.auth = auth
            self.params = params
            self.headers = headers
            self.json = json


class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.text = json.dumps(json_data)
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.fixture(scope='module')
def uaa_client():
    auth_config = AuthClientConfig(
        client_id="test",
        client_secret="test",
        auth_host="http://test")
    client = UaaClient(auth_config)
    return client


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"email": "Test"}, 200)])
def test_get_check_token_response_returns_tenant(post, uaa_client):
    """
    get_check_token_response() should return default tenant Nervana Systems
    """
    token_payload = uaa_client.get_check_token_response("")

    assert (token_payload.tenant == "Nervana Systems")


@pytest.mark.parametrize("value",    # noqa
                         [MockResponse({"id_token": "Test"}, 200)])
def test_get_id_token_request(post, uaa_client):
    """
    get_id_token() should set response_type to id_token
    """
    data = {}

    uaa_client.get_id_token(data)
    expected = {
        "client_id": "test",
        "client_secret": "test",
        "scope": "openid",
        "grant_type": "password",
        "response_type": "id_token"
    }

    assert (post.data == expected)


@pytest.mark.parametrize("value", [MockResponse({'code': 'fake-code'},  # noqa
                                                201)])
def test_get_password_reset_url(monkeypatch, post, uaa_client):
    """
    get_password_reset_url() should return a following URL:
     <reset_password_endpoint>/<reset_code>, where reset_code is obtained from
     UAA in _get_password_reset_code() method.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_code = 'fake-code'

    expected_url = '{reset_password_endpoint}?code={code}'.format(
        reset_password_endpoint=uaa_client.password_reset_endpoint,
        code=fake_code)

    assert expected_url == uaa_client.get_password_reset_url()


@pytest.mark.parametrize("value", [MockResponse(None,  # noqa
                                                500)])
def test_get_password_reset_url_failure(monkeypatch, post, uaa_client):
    """
    get_password_reset_url() should return a following URL:
     <reset_password_endpoint>/<reset_code>, where reset_code is obtained from
     UAA in _get_password_reset_code() method.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    assert uaa_client.get_password_reset_url() is None


@pytest.mark.parametrize("value",  # noqa
                         [MockResponse({"resources": [{"id": "fake-id"}]},
                                       200)])
def test_get_userid(monkeypatch, get, uaa_client):
    """
    get_userid() should create a GET /Users request with proper filter and
    return email of found user.
    """
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_email = "test@test.com"
    found_id = uaa_client.get_userid(email=fake_email)

    expected_params = {'filter': 'email eq "{}"'.format(fake_email)}
    assert expected_params == get.params
    assert found_id == fake_email


@pytest.mark.parametrize("value", [MockResponse(None, 500)])  # noqa
def test_get_userid_failure(monkeypatch, get, uaa_client):
    monkeypatch.setattr('nauth.clients.uaa_client.UaaClient._get_auth_header',
                        lambda *args, **kwargs: None)

    fake_email = "test@test.com"
    found_id = uaa_client.get_userid(email=fake_email)
    assert found_id is None
