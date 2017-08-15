# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2017 Datmellow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import datetime
import logging
import aiohttp
import typing
import copy

from league import __version__
from league import errors
from collections import Counter
from .enums import RouteVersions

log = logging.getLogger(__name__)


class RateLimitHandler:
    def __init__(self, headers: aiohttp.ClientResponse.headers):
        self.limits = []
        self.limit_extractor(headers)
        self.count_extractor(headers)
        self.last_request = datetime.datetime.utcnow()
        self.locked = asyncio.Event()
        self.cool_down = 0

    def limit_extractor(self, headers):
        limits = []
        if headers.get('X-App-Rate-Limit'):
            limit_header = headers.get('X-App-Rate-Limit').split(",")
            for l in limit_header:
                max_calls, per_second = l.split(":")
                limits.append(
                    {"max": int(max_calls), "per_interval": int(per_second),
                     "next_reset": datetime.datetime.utcnow() + datetime.timedelta(seconds=int(per_second)),
                     "amount": 0}
                )
            self.limits = limits

    def count_extractor(self, headers):
        new_limit = []
        if headers.get('X-App-Rate-Limit'):
            limit_header = headers.get('X-App-Rate-Limit-Count').split(",")
            for l in limit_header:
                for limit in self.limits:
                    amount, interval = l.split(":")
                    if limit['per_interval'] == int(interval):
                        limit['amount'] = int(amount)
                        limit['next_reset'] = datetime.datetime.utcnow() - datetime.timedelta(
                            seconds=int(interval))
                        new_limit.append(limit)
            self.limits = new_limit

    @asyncio.coroutine
    def cool_down_handler(self):
        self.locked.clear()
        yield from asyncio.sleep(self.cool_down)
        self.locked.set()

    @asyncio.coroutine
    def processor(self):
        yield from self.locked.wait()
        for limit in self.limits:
            if datetime.datetime.utcnow() < limit['next_reset']:
                limit['next_reset'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=limit['per_interval'])
                limit['amount'] = 0
            elif limit['amount'] + 2 >= limit['max']:
                time_to_sleep = datetime.datetime.utcnow() - limit['next_reset']
                log.warning(" {0} limit reached - Waiting {1}".format(limit['amount'], time_to_sleep.total_seconds()))
                self.cool_down = time_to_sleep.total_seconds()
                yield from self.cool_down_handler()
                limit['next_reset'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=limit['per_interval'])
                limit['amount'] = 0
            else:
                limit['amount'] += 1
        self.last_request = datetime.datetime.utcnow()
        return


class Statistics:
    def __init__(self):
        self.requests = 0
        self.endpoints = Counter()
        self.responses = Counter()

    def new_request(self, method, response):
        self.requests += 1
        self.endpoints[method] += 1
        if response is not None:
            self.responses[response] += 1


class Bucket:
    """Represents an abstraction of region/method api usage tracking. Used to keep track of api limits"""

    def __init__(self, region: str, session: aiohttp.ClientSession, api_key: str,
                 rate_limits: typing.List[typing.Tuple[int, int]]):
        self.base = "https://{0}.api.riotgames.com/lol/".format(region)
        self.handlers = {}  # type: typing.Dict[str,RateLimitHandler]
        self._session = session  # type: aiohttp.ClientSession
        self._api_key = api_key  # type: typing.Text
        self._rate_limits = rate_limits  # type: typing.List[typing.Tuple[int,int]]
        self.statistics = Statistics()

    @staticmethod
    def clean_params(data):
        if len(data) == 0:
            return {}
        for k, v in data.items():
            if v is True:
                data[k] = "true"
            elif v is False:
                data[k] = "false"
        return data

    def route_builder(self, method, route):
        url = "{base}{method}/{version}/{route}".format(base=self.base, method=method,
                                                        version=RouteVersions[method.replace("-", "_")].value,
                                                        route=route)
        return url

    @asyncio.coroutine
    def raw_request(self, url) -> dict:
        response = yield from self._session.get(url)
        if response.status == 200:
            data = yield from response.json()
            return data

    @asyncio.coroutine
    def error_handler(self, response: aiohttp.ClientResponse, method):
        if response.status == 400:
            try:
                raise errors.BadRequest
            except errors.BadRequest as e:
                log.error(e, exc_info=True)
        elif response.status == 403:
            raise errors.UnAuthorized
        elif response.status == 404:
            raise errors.EmptyResponse
        elif response.status == 422:
            raise errors.InactivePlayer
        elif response.status == 429:
            cooldown = int(response.headers.get("Retry-After"))
            log.error(" 429 - Rate limited for {0} seconds on method {1}".format(cooldown, method))
            self.handlers[method].cool_down = cooldown
            yield from self.handlers[method].cool_down_handler()
        elif response.status in [500, 502, 503, 504]:
            raise errors.ServiceUnavailable

    @asyncio.coroutine
    def request(self, method: str, route: str, **kwargs) -> typing.Union[dict, None]:
        url = self.route_builder(method, route)
        cleaned_params = self.clean_params(kwargs)
        method_obj = self.handlers.get(method)
        try:
            if method_obj is not None:
                yield from asyncio.wait_for(method_obj.processor(), timeout=None)
            log.info("Requesting data from endpoint - {0}".format(method))
            response = yield from self._session.get(url, params=cleaned_params,
                                                    headers={"X-Riot-Token": self._api_key,
                                                             "User-Agent": "Using : League.py/{0}".format(
                                                                 __version__)})  # type: aiohttp.ClientResponse
            log.info("{0} - Response on Method {1}".format(response.status, method))
            if response.status == 200:
                if method_obj is None:
                    self.handlers[method] = RateLimitHandler(response.headers)
                    self.handlers[method].locked.set()
                elif method_obj is not None:
                    method_obj.count_extractor(response.headers)
                data = yield from response.json()  # type: dict
                return data
            else:
                yield from self.error_handler(response, method)
        finally:
            self.statistics.new_request(method, response)
            if asyncio.iscoroutinefunction(response.close):
                yield from response.close()
            else:
                response.close()
