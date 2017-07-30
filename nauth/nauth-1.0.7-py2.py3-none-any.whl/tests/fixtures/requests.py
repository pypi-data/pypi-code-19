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

import pytest


class FakeRequest(object):
    def __init__(self, url="", data="", auth="", params="", headers="",
                 json=""):
            self.url = url
            self.data = data
            self.auth = auth
            self.params = params
            self.headers = headers
            self.json = json


@pytest.fixture
def post(monkeypatch, value):
    fp = FakeRequest()

    def post(url, data="", auth="", params="", json="", headers=""):
        fp.url = url
        fp.data = data
        fp.auth = auth
        fp.params = params
        fp.json = json
        fp.headers = headers
        return value

    monkeypatch.setattr('requests.post', post)
    return fp


@pytest.fixture
def get(monkeypatch, value):
    fg = FakeRequest()

    def get(url, data="", params="", headers=""):
        fg.url = url
        fg.data = data
        fg.params = params
        fg.headers = headers
        return value

    monkeypatch.setattr('requests.get', get)
    return fg


@pytest.fixture
def delete(monkeypatch, value):
    fd = FakeRequest()

    def delete(url, data="", params="", headers=""):
        fd.url = url
        fd.data = data
        fd.params = params
        fd.headers = headers
        return value

    monkeypatch.setattr('requests.delete', delete)
    return fd
