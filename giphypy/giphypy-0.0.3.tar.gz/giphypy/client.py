import asyncio
from typing import Optional

import aiohttp

from .constants import API_URL, STICKERS_URL
from .errors import GiphyPyError, GiphyPyKeyError
from .utils import output_links


class Giphy:
    """
    Wrapper for the Giphy api. Keys can be optained from:
    https://developers.giphy.com
    """
    def __init__(self, api_key,
                 loop: Optional[asyncio.BaseEventLoop] = None,
                 session: aiohttp.ClientSession = None,
                 stickers=False):
        """
        :param api_key: Giphy API key, required.
        """
        if not api_key:
            raise GiphyPyKeyError

        self.api_key = api_key
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)
        self.params = {
            'api_key': self.api_key,
        }
        self.stickers = stickers

    async def _get(self, api_endpoint: str, **kwargs):
        """
        Wrapper for fetching data from Giphy
        :param api_endpoint: Giphy API endpoint, usually search or translate.
        """
        req_str = API_URL + api_endpoint
        if self.stickers:
            req_str = STICKERS_URL + api_endpoint
        async with self.session.get(url=req_str, params=self.params) as resp:
            data = await resp.json()
            self.session.close()
        return data

    async def search(self, query: str, **kwargs):
        """
        Main search method for Giphy's search endpoint
        :param query: search term, Required
        :param limit: search result limit, not Required
        :param offset: search result offset
        :param rating: search result age rating (Y, G, PG, PG-13, R)
        :param lang: language, default=en
        """

        if kwargs:
            self.params.update(**kwargs)

        self.params['q'] = query
        data = await self._get('search', params=self.params)
        if data['meta']['status'] is not 200:
            raise GiphyPyError(str(data['meta']['msg']))

        return data

    async def translate(self, s: str):
        """
        :param s: Search term, Required
        :return: dict object
        """
        self.params['s'] = s

        data = await self._get('translate', params=self.params)

        if data['meta']['status'] is not 200:
            raise GiphyPyError(str(data['meta']['msg']))
        return data

    async def gif_links(self, query: str, **kwargs):
        """
        :param query: Search by query.
        :param kwargs: limit/offset/rating/lang
        :return: an array with gif links
        """
        data = await self.search(query, **kwargs)
        return output_links(data)

    async def random(self, **kwargs):
        """
        :param kwargs: tag/rating/fmt
        :return: an dict object with data
        """
        if kwargs:
            self.params.update(**kwargs)

        data = await self._get('random', params=self.params)
        return data

    async def find_by_id(self, gif_id: str):
        """
        :param gif_id: an gif ID
        :return: dict object with data
        """
        data = await self._get(f'{gif_id}', params=self.params)
        return data

    async def trending(self, **kwargs):
        """
        :param kwargs: rating/search limit
        :return: List of top trending gifs
        """
        if kwargs:
            self.params.update(**kwargs)
        data = await self._get('trending', params=self.params)
        return data

    async def stickers_search(self, query: str, **kwargs):
        """
        :param query: Find by query
        :param kwargs: title/limit/offset/rating/lang/fmt
        :return: an dict object with data
        """
        self.params['q'] = query
        if kwargs:
            self.params.update(**kwargs)

        data = await self._get('search', params=self.params)
        return data

    async def stickers_trending(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        if kwargs:
            self.params.update(**kwargs)
        data = await self._get('trending', params=self.params)
        return data

    async def stickers_links(self, query: str, **kwargs):
        """
        :param query: Find by query
        :param kwargs: title/limit/offset/rating/lang/fmt
        :return: an dict object with data
        """
        data = await self.stickers_search(query, **kwargs)
        return output_links(data)

    async def stickers_translate(self, s: str):
        """
        :param s: string for example 'ryan hosling'
        :return: an object with data
        """
        data = await self.translate(s)
        return data

    async def stickers_random(self, **kwargs):
        """
        :param kwargs: tag/rating/fmt
        :return: an object with data
        """
        if kwargs:
            self.params.update(**kwargs)
        data = await self.random(params=self.params)
        return data
