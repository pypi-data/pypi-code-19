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
import datetime
from league.http import Bucket
import importlib
import typing


class RiotDto:
    """

    Attributes
    ----------
    raw_response : dict
        The Raw response for the obj returned by the API
    timestamp : datetime.datetime
        The UTC timestamp when this object was created


    """

    def __init__(self, **kwargs):
        self.__bucket__ = kwargs.get('bucket')  # type: Bucket
        self.__static_cache__ = kwargs.get('cache')  # type: dict
        self.__data_cache__ = kwargs.get('data_cache')  # type: typing.Dict[typing.Any,typing.Any]
        self.__injector__ = kwargs.get('injector')
        self.raw_response = kwargs.get('raw_response')  # type: dict
        self.timestamp = datetime.datetime.utcnow()

    @staticmethod
    def get_object(wanted_obj: str, data: dict) -> typing.Union[object, None]:
        if data is None:
            return None
        my_class = getattr(importlib.import_module("league"), wanted_obj)
        if my_class is None:
            return None
        return my_class(**data)

    def get_from_cache(self, cache: str, item_id: typing.Union[int, str]):
        if cache in self.__static_cache__:
            if len(self.__static_cache__.get(cache)) > 0:
                tmp_cache = self.__static_cache__.get(cache)
                if tmp_cache:
                    return tmp_cache.get(item_id)
                else:
                    return item_id
            else:
                return item_id
        else:
            return item_id
