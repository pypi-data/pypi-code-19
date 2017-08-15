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
import copy
import logging

import aiohttp
import typing

from league.enums import *
from league.http import Bucket
from league.leagues import League
from league.match import Match, PartialMatch
from league.static_data import Champion, Rune, Item, Map, SummonerMastery, Image
from league.status import Shard
from league.summoner import Summoner
from league import errors

log = logging.getLogger(__name__)


class Client:
    """Represents the main client of league.py

    Parameters
    ----------
    api_key : str
        The API key for accessing riot's servers.
    rate_limit: Optional[list[tuple]]
        The rate limits the Client should abide by. eg [(20,1),(100,180)]
    session: Optional[client session]
        the `client session`_ to use for web operations. Defaults to ``None``,
        in which case a ClientSession is created.
    static_cache : Optional[dict]
        The cache of all static data the client will use. Must be in the form Riot returns from the static-data
        endpoints or from Data-Dragon urls
    data_cache : Optional[dict]
        The cache of all results the library has returned in their respective object form.

    Note
    ----
    The default rate limit is **20** requests per **second** and **100** requests per **180 seconds**.


    .. _client session: http://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientSession

    """

    def __init__(self, api_key: str, *, session: aiohttp.ClientSession = None,
                 rate_limit: typing.List[typing.Tuple[int, int]] = None,
                 static_cache: typing.Dict = None, data_cache: typing.Dict = None):
        if rate_limit is None:
            rate_limit = [(20, 1), (100, 120)]
        self._session = aiohttp.ClientSession() if session is None else session  # type: aiohttp.ClientSession
        self._buckets = {item.name: Bucket(item.value, self._session, api_key, rate_limit) for item in
                         Regions}  # type: typing.Dict[str,Bucket]
        self.static_cache = static_cache if static_cache \
                                            is not None else {}  # type: typing.Dict[str,typing.Dict[int,object]]
        self.data_cache = data_cache if data_cache is not None else {}

    @asyncio.coroutine
    def cache_setup(self, locale: str = "en_US"):
        for item in ['champions', 'runes', 'items', 'maps', 'masteries', 'profile_icons']:
            if item not in self.static_cache:
                for region in Regions:
                    try:
                        func = getattr(self, "get_all_{}".format(item))
                        if func is not None:
                            data = yield from func(region=region, locale=locale)
                            if data is not None:
                                self.static_cache[item] = data
                                break
                            else:
                                break
                        else:
                            break
                    except errors.ServiceUnavailable:
                        continue
                    except errors.UnAuthorized:
                        return
                    except errors.RateLimited:
                        continue

    def _data_injector(self, bucket: Bucket = None, data=None):
        new_data = copy.copy(data)
        new_data['bucket'] = bucket
        new_data['raw_response'] = data
        if hasattr(self, 'static_cache'):
            new_data['cache'] = self.static_cache
        elif hasattr(self, '__static_cache__'):
            new_data['cache'] = getattr(self, "__static_cache__")
        if hasattr(self, '_data_injector'):
            new_data['injector'] = self._data_injector
        elif hasattr(self, "__injector__"):
            new_data['injector'] = getattr(self, "__injector__")
        return new_data

    def __del__(self):
        if not self._session.closed:
            if asyncio.iscoroutinefunction(self._session.close):
                asyncio.async(self._session.close())
            else:
                self._session.close()

    @asyncio.coroutine
    def get_summoner(self, *, summoner_id: int = None, summoner_name: str = None, account_id: int = None,
                     region: Regions = Regions.na) -> Summoner:
        """|coro|

        Searches for a summoner based on any given input, the order of parameters is based on the search order.


        Parameters
        ----------
        summoner_id : int
            The ID of the summoner to lookup
        summoner_name : str
            The summoner name to lookup
        account_id : int
            The account ID of the summoner to lookup
        region : :class:`Regions`
            The region to get the summoner from

        Returns
        -------
        :class:`Summoner`
            The summoner associated with the parameters given.

        Raises
        ------
        :class:`NoSummonerFound`
            Indicates If the api doesn't return any results
        """
        base_route = "summoners"
        if account_id is not None:
            route = "{0}/by-account/{1}".format(base_route, account_id)
        elif summoner_id is not None:
            route = "{0}/{1}".format(base_route, summoner_id)
        elif summoner_name is not None:
            route = "{0}/by-name/{1}".format(base_route, summoner_name)
        else:
            raise ValueError("Incorrect value passed")
        bucket = self._buckets[region.name]
        data = yield from bucket.request("summoner", route)
        if data is not None:
            return Summoner(region=region, **self._data_injector(bucket=bucket, data=data))

    @asyncio.coroutine
    def get_match(self, *, match_id: typing.Union[int, PartialMatch], region: Regions = Regions.na) -> Match:
        """|coro|

        Searches for a match using the matchID/region pair provided

        Parameters
        ----------
        match_id : Union[int,:class:`PartialMatch`]
            The ID of the match to lookup
        region : :class:`Regions`
            the region the match belongs too

        Returns
        -------
        :class:`Match`
            The Match with the ID given.

        Raises
        ------
        :class:`NoMatchFound`
            Indicates if the API did not return any results.
        """
        if isinstance(match_id, int):
            route = "matches/{0}".format(match_id)
        elif isinstance(match_id, PartialMatch):
            route = "matches/{0}".format(match_id.match_id)
        data = yield from self._buckets[region.name].request("match", route)
        if data is not None:
            return Match(**self._data_injector(self._buckets[region.name], data))

    @asyncio.coroutine
    def get_match_timeline(self, *, match_id: typing.Union[int, Match], region: Regions = Regions.na):
        """

        Parameters
        ----------
        match_id : Union[int,:class:`PartialMatch`]
            The ID of the match to lookup
        region : :class:`Regions`
            the region the match belongs too

        Returns
        -------

        """
        if isinstance(match_id, int):
            m_id = match_id
        elif isinstance(match_id, PartialMatch):
            m_id = match_id.match_id
        route = "timelines/by-match/{0}".format(m_id)
        data = yield from self._buckets[region.name].request("match", route)
        if data is not None:
            return PartialMatch(**self._data_injector(self._buckets[region.name], data))

    def get_requests_statistics(self, *, region: Regions = Regions.na) -> typing.Dict[
        str, int]:
        """
        Retrieves request statistics for a certain region used by the :class:`Client` thus far

        Parameters
        ----------
        region : :class:`Regions`
            the region to lookup stats

        Returns
        -------
        dict
            dictionary containing:
                * total : int total amount of requests made across all regions
                * routes : dict with routes and how many requests were made by each

        """
        return self._buckets[region.name].statistics

    @asyncio.coroutine
    def get_challenger(self, *, queue_type: Queue = Queue.ranked_solo, region: Regions = Regions.na) -> League:
        """|coro|

        Gets the :class:`League` of the challenger league for the specified region.

        Parameters
        ----------
        queue_type : :class:`Queue`
            The queue type to get challenger league for.
        region : :class:`Regions`
            The Region to lookup challenger for.
        Returns
        -------
        :class:`League`
            A League that contains everyone in challenger league

        """
        route = "challengerleagues/by-queue/{0}".format(queue_type.value)
        data = yield from self._buckets[region.name].request("league", route)
        if data is not None:
            return League(**self._data_injector(self._buckets[region.name], data))

    @asyncio.coroutine
    def get_champion_by_name(self, *, name: str, ignore_cache: bool = False, region: Regions = Regions.na,
                             locale: str = "en_US") -> Champion:
        """|coro|

        Gets the :class:`Champion` using the name given

        Parameters
        ----------
        name : str
            The Name of the champion you want to lookup
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.


        Returns
        -------
        :class:`Champion`

        Raises
        ------
        ValueError
            if no champion data is found

        """
        if not self.static_cache.get('champions') or ignore_cache:
            route = "champions"
            data = yield from self._buckets[region.name].request("static-data", route, dataById=True,
                                                                 locale=locale,
                                                                 tags="all")
            if data is not None:
                for cdata in data['data'].values():
                    if cdata['name'].lower() == name.lower():
                        route = "champions/{0}".format(cdata['id'])
                        ddata = yield from self._buckets[Regions.na.name].request("static-data", route)
                        if ddata is not None:
                            objdata = {}
                            objdata.update(cdata)
                            objdata.update(data)
                            objdata.update(ddata)
                        else:
                            return Champion(**self._data_injector(self._buckets[region.name], objdata))

            else:
                raise ValueError("Champion name not found")
        else:
            for champ in self.static_cache['champions'].values():
                if name.lower() == champ.name.lower():
                    return champ
            else:
                raise ValueError("Champion name not found")

    @asyncio.coroutine
    def get_champion_by_id(self, *, cid: int, ignore_cache: bool = False, region: Regions = Regions.na,
                           locale: str = "en_US") -> Champion:
        """|coro|

        Gets the :class:`Champion` by the ID provided

        Parameters
        ----------
        cid : int
            The Champion ID to lookup
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.


        Returns
        -------
        :class:`Champion`

        Raises
        ------
        ValueError
            if no champion data is found

        """
        if not self.static_cache.get('champions') or ignore_cache:
            mydata = {}
            route = "champions/{0}".format(cid)
            data = yield from self._buckets[region.name].request("static-data", route, dataById=True,
                                                                 locale=locale,
                                                                 tags="all")
            if data is None:
                raise ValueError("Champion id not found")
            mydata.update(data)
            route = "champions/{0}".format(cid)
            ddata = yield from self._buckets[Regions.na.name].request("platform", route)
            mydata.update(ddata)
            return Champion(**self._data_injector(self._buckets[region.name], mydata))
        else:
            data = self.static_cache['champions'].get(cid)
            if data is not None:
                return data
            else:
                raise ValueError("Champion id not found")

    @asyncio.coroutine
    def get_all_champions(self, *, ignore_cache=False, region: Regions = Regions.na,
                          locale: str = "en_US") -> typing.Dict[int, Champion]:
        """|coro|

        Grabs all the champions.

        Parameters
        ----------
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        dict : champion_id : :class:`Champion`
            Returns all champions in the game

        """
        if not self.static_cache.get('champions') or ignore_cache:

            base_route = "champions"
            champions = []
            base_data = yield from self._buckets[region.name].request("platform", base_route)
            other_data = yield from self._buckets[region.name].request("static-data", base_route, dataById=True,
                                                                       locale=locale, tags="all")
            if all([base_data, other_data]):
                for champ in base_data['champions']:
                    combined_data = {}
                    combined_data.update(champ)
                    combined_data.update(other_data['data'][str(champ['id'])])
                    champions.append(Champion(**self._data_injector(self._buckets[region.name], combined_data)))
                champ_data = {}
                for champion in champions:
                    champ_data[champion.cid] = champion
                return champ_data

            else:
                return None
        else:
            return self.static_cache['champions']

    @asyncio.coroutine
    def get_all_runes(self, *, ignore_cache: bool = False, region: Regions = Regions.na,
                      locale: str = "en_US") -> typing.Dict[int, Rune]:
        """|coro|

        Retrieves all the runes from the API.

        Parameters
        ----------
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        dict : {rune_id : :class:`Rune`}

        """
        if not self.static_cache.get('runes') or ignore_cache:
            base_data = yield from self._buckets[region.name].request("static-data", 'runes', locale=locale,
                                                                      tags='all')
            if base_data is not None:
                response = {}
                for key, value in base_data['data'].items():
                    response[int(key)] = Rune(**self._data_injector(self._buckets[region.name], value))
                return response

        else:
            return self.static_cache['runes']

    @asyncio.coroutine
    def get_rune_by_id(self, *, rune_id: int, ignore_cache: bool = False, region: Regions = Regions.na,
                       locale: str = "en_US") -> Rune:
        """|coro|

        Parameters
        ----------
        rune_id : int
            The id of the rune to lookup
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        :class:`Rune`

        """
        if not self.static_cache.get('runes') or ignore_cache:
            base_data = yield from self._buckets[region.name].request("static-data", 'runes/{0}'.format(rune_id),
                                                                      locale=locale, tags="all")
            if base_data is not None:
                return Rune(**self._data_injector(self._buckets[region.name], base_data))

        else:
            return self.static_cache['runes'].get(rune_id)

    @asyncio.coroutine
    def get_all_items(self, *, region: Regions = Regions.na, ignore_cache: bool = False,
                      locale: str = "en_US") -> typing.Dict[int, Item]:
        """|coro|

        Retrieves all the items from the API.

        Parameters
        ----------
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        dict : {item_id : :class:`Item`}

        """
        if not self.static_cache.get('items') or ignore_cache:
            base_data = yield from self._buckets[region.name].request("static-data", 'items', locale=locale,
                                                                      tags="all")
            if base_data is not None:
                response = {}
                for key, value in base_data['data'].items():
                    response[int(key)] = Item(**self._data_injector(self._buckets[region.name], value))
                for item, value in response.items():
                    new_data = []
                    if value.recipe is not None:
                        for p in value.recipe:
                            new_data.append(response.get(int(p)))
                        value.recipe = new_data
                    new_data.clear()
                    if value.into is not None:
                        for p in value.into:
                            new_data.append(response.get(int(p)))
                            value.into = new_data
                return response
        else:
            return self.static_cache['items']

    @asyncio.coroutine
    def get_item_by_id(self, *, item_id: int, region: Regions = Regions.na, ignore_cache: bool = False,
                       locale: str = "en_US") -> Item:
        """|coro|

        Gets the item by its ID

        Parameters
        ----------
        item_id : int
            The item's ID
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        :class:`Item`

        """
        if not self.static_cache.get('items') or ignore_cache:

            base_data = yield from self._buckets[region.name].request("static-data", 'items/{0}'.format(item_id),
                                                                      locale=locale, tags="all")
            if base_data is not None:
                return Item(**self._data_injector(self._buckets[region.name], base_data))
        else:
            return self.static_cache['items'].get(item_id)

    @asyncio.coroutine
    def get_item_by_name(self, *, name: str, region: Regions = Regions.na, ignore_cache: bool = False,
                         locale: str = "en_US") -> Item:
        """|coro|

        Gets the item by its name

        Parameters
        ----------
        name: str
            the name of the item to look for.
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        :class:`Item`

        """
        if not self.static_cache.get('items') or ignore_cache:
            base_data = yield from self._buckets[region.name].request("static-data", 'items', locale=locale,
                                                                      tags="all")
            if base_data is not None:
                for key, value in base_data['data'].items():
                    if value['name'].lower() == name.lower():
                        return Rune(**self._data_injector(self._buckets[region.name], base_data))

        else:
            for item in self.static_cache.get('items').values():
                if item.name.lower() == name.lower():
                    return item

    @asyncio.coroutine
    def get_status(self, *, region: Regions = Regions.na) -> Shard:
        """|coro|


        Gets shard status for a specific region.


        Parameters
        ----------
        region : :class:`Regions`
            the server shard to lookup

        Returns
        -------
        :class:`Shard`

        """
        method = "status"
        endpoint = "shard-data"
        data = yield from self._buckets[region.name].request(method, endpoint)
        if data is not None:
            return Shard(**self._data_injector(self._buckets[region.name], data))

    @asyncio.coroutine
    def get_all_maps(self, *, region: Regions = Regions.na, ignore_cache: bool = False,
                     locale: str = "en_US") -> typing.Dict[int, Map]:
        """

        Parameters
        ----------
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        dict : map_id : :class:`Map`

        """
        if not self.static_cache.get('maps') or ignore_cache:
            data = yield from self._buckets[region.name].request("static-data", "maps", locale=locale)
            if data is not None:
                maps = {}
                for m in data['data']:
                    obj = Map(**self._data_injector(self._buckets[region.name], data['data'][m]))
                    maps[m] = obj
                return maps

        else:
            return self.static_cache['maps']

    @asyncio.coroutine
    def get_all_masteries(self, *, region: Regions = Regions.na, ignore_cache: bool = False,
                          locale: str = "en_US") -> typing.Dict[int, SummonerMastery]:
        """

        Parameters
        ----------
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        dict : mastery_id : :class:`SummonerMastery`

        """
        if not self.static_cache.get('masteries') or ignore_cache:
            data = yield from self._buckets[region.name].request("static-data", "masteries", locale=locale, tags='all')
            if data is not None:
                masteries = {}
                for m in data['data']:
                    obj = SummonerMastery(**self._data_injector(self._buckets[region.name], data['data'][m]))
                    masteries[int(m)] = obj
                return masteries

        else:
            return self.static_cache['masteries']

    @asyncio.coroutine
    def get_all_profile_icons(self, *, region: Regions = Regions.na, ignore_cache: bool = False,
                              locale: str = "en_US") -> typing.Dict[int, Image]:
        """

        Parameters
        ----------
        ignore_cache : Bool
            Tells the function to ignore the cache and request the data from the API.
        region : :class:`Regions`
            The region to get the call against.
        locale : str
            Locale code for returned data.

        Returns
        -------
        dict : icon_id : :class:`Image`


        """
        if not self.static_cache.get('icons') or ignore_cache:
            data = yield from self._buckets[region.name].request("static-data", "profile-icons", locale=locale,
                                                                 tags='all')
            if data is not None:
                profile_icons = {}
                for icon in data['data']:
                    obj = Image(**self._data_injector(self._buckets[region.name], data['data'][icon]['image']))
                    profile_icons[int(icon)] = obj
                return profile_icons
        else:
            return self.static_cache['profile_icons']
