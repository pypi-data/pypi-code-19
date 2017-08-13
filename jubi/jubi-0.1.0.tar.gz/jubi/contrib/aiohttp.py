# -*- coding: utf-8 -*-
import asyncio
from typing import Any, Dict

import aiohttp

from jubi.abc import Requester, Response


class Aiohttp(Requester):
    def __init__(self, session: aiohttp.ClientSession, *args: Any,
                 **kwargs: Any) -> None:
        self._session = session
        super().__init__(*args, **kwargs)

    async def request(self, method: str, url: str, headers: Dict,
                      body: bytes = b'') -> Response:
        async with self._session.request(method, url, headers=headers,
                                         data=body) as response:
            return Response(
                status=response.status,
                headers=response.headers,
                body=await response.read(),
            )

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)
