# -*- coding: utf-8 -*-
import abc
import json
from typing import Dict

import attr


@attr.s
class Response:
    status: str = attr.ib()
    headers: Dict = attr.ib()
    body: bytes = attr.ib()

    def json(self):
        return json.loads(self.body)


class Requester(abc.ABC):

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def request(self, method: str, url: str, headers: Dict,
                      body: bytes = b'') -> Response:
        pass

    @abc.abstractmethod
    async def sleep(self, seconds: float):
        pass
