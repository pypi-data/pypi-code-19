# -*- coding: utf-8 -*-
from typing import Any, Dict
from urllib.parse import urlencode

from yunpian.abc import Requester, Response
from yunpian.utils import format_url, create_headers


class Client:
    CONTENT_TYPE = 'application/x-www-form-urlencoded'

    def __init__(self, requester: Requester, api_key: str):
        self._api_key = api_key
        self.requester = requester

    async def _make_request(self, method: str, url: str, url_params: Dict,
                            data: Any) -> Response:
        filled_url = format_url(url, url_params)
        request_headers = create_headers(self._api_key)

        if isinstance(data, dict):
            request_headers['content-type'] = self.CONTENT_TYPE
            body = urlencode(data)
        else:
            body = data
        response = await self.requester.request(
            method, filled_url, request_headers, body
        )
        return response

    async def get(self, url: str, url_params: Dict) -> Response:
        return await self._make_request('GET', url, url_params, b'')

    async def post(self, url: str, url_params: Dict, *, data: Any) -> Response:
        return await self._make_request('POST', url, url_params, data)

    async def put(self, url: str, url_params: Dict, *, data: Any) -> Response:
        return await self._make_request('PUT', url, url_params, data)

    async def patch(self, url: str, url_params: Dict, *, data: Any
                    ) -> Response:
        return await self._make_request('PATCH', url, url_params, data)

    async def delete(self, url: str, url_params: Dict):
        return await self._make_request('DELETE', url, url_params, b'')
