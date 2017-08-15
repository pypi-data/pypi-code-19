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

import typing

from league.errors import EmptyResponse
from league.leagues import LeagueEntry, League
from league.mastery import ChampionMastery
from league.match import PartialMatch
from league.spectator import LiveMatch
from league.static_data import Champion, RunePage, MasteryPage
from league.riotDTO import RiotDto


class Summoner(RiotDto):
    """Basic Representation of a league summoner


    Attributes
    ----------
    sid: int
        Summoner ID.

    name: str
        Summoner name.

    icon: int
        ID of the summoner icon associated with the summoner.

    level: int
        Summoner level associated with the summoner.

    revision_date: `datetime.datetime`
        when profile was last modified in UTC.

    account_id: int
        Account ID.

    region: :class:`Regions`
        The region the summoner belongs to.
    """

    def __init__(self, **kwargs):
        super(Summoner, self).__init__(**kwargs)
        self.sid = kwargs.get('id', kwargs.get('summonerId', {}))
        self.name = kwargs.get('name', kwargs.get('summonerName', {}))
        self.icon = self.get_from_cache("profile_icons", kwargs.get('profileIconId'))
        self.level = kwargs.get('summonerLevel')
        if kwargs.get('revisionDate'):
            date = kwargs.get('revisionDate') / 1000
            self.revision_date = datetime.datetime.utcfromtimestamp(date)
        else:
            self.revision_date = None
        self.account_id = kwargs.get('accountId')
        self.region = kwargs.get('region')

    def __eq__(self, other):
        if isinstance(other, Summoner):
            if self.sid == getattr(other, "sid"):
                return True
            elif self.account_id == getattr(other, "account_id"):
                return True
            else:
                return False

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @asyncio.coroutine
    def current_match(self) -> typing.Union[LiveMatch, None]:
        """|coro|

        Get the summoners current match. If any

        Returns
        -------
        union[:class:`LiveMatch`,None]
            The live match of the summoner if found, else returns None

        """
        endpoint = "active-games/by-summoner/{0}".format(self.sid)
        try:
            data = yield from self.__bucket__.request("spectator", endpoint)
            if data is not None:
                return LiveMatch(**self.__injector__(data=data))
        except EmptyResponse:
            return None

    @asyncio.coroutine
    def ranked_data(self) -> typing.List[LeagueEntry]:
        """|coro|


        retrieves all league entry data for all ranked queue types.

        Returns
        -------
        list[:class:`LeagueEntry`]
            All league data that the summoner belongs to.

        """
        endpoint = "positions/by-summoner/{0}".format(self.sid)
        data = yield from self.__bucket__.request("league", endpoint)
        if data is not None:
            return [LeagueEntry(**self.__injector__(data=league)) for league in data]
        else:
            return None

    @asyncio.coroutine
    def champion_masteries(self) -> typing.List[ChampionMastery]:
        """|coro|

        Get all of the masteries for the specified :class:`Summoner`

        Returns
        -------
        list[:class:`ChampionMastery`]
            A list of masteries for the specific summoner


        """
        route = "champion-masteries/by-summoner/{0}".format(self.sid)
        data = yield from self.__bucket__.request("champion-mastery", route)
        if data is not None:
            return [
                ChampionMastery(summoner=self, champion=self.get_from_cache('champions', champ['championId']),
                                **self.__injector__(data=champ))
                for
                champ in data]

    @asyncio.coroutine
    def champion_mastery(self, *, champion: typing.Union[Champion, int]) -> ChampionMastery:
        """|coro|

        Gets a mastery for a specified champion

        Parameters
        ----------
        champion : Union[:class:`Champion`,int]
            The champion to lookup

        Returns
        -------
        :class:`ChampionMastery`
            The mastery of the specified champion

        """

        route = "champion-masteries/by-summoner/{0}/by-champion/{1}".format(self.sid,
                                                                            getattr(champion, 'cid', champion))
        data = yield from self.__bucket__.request("champion-mastery", route)
        if data is not None:
            return ChampionMastery(summoner=self, champion=champion, **self.__injector__(data=data))

    @asyncio.coroutine
    def champion_mastery_score(self) -> int:
        """|coro|

        Gets the summoner's total mastery score

        Returns
        -------
        int
            Summoners total mastery score

        """
        route = "scores/by-summoner/{0}".format(self.sid)
        data = yield from self.__bucket__.request("champion-mastery", route)
        if data is not None:
            return data

    @asyncio.coroutine
    def recent_matches(self) -> typing.List[PartialMatch]:
        """|coro|


        Retrieves the last 20 matches for the summoner


        Returns
        -------
        list[:class:`PartialMatch`]
            A List of the 20 past matches played.

        """
        route = "matchlists/by-account/{0}/recent".format(self.account_id)
        data = yield from self.__bucket__.request("match", route)
        if data is not None:
            formated_data = []
            for match in data['matches']:
                champion = self.get_from_cache('champions', match['champion'])
                match['champion'] = champion
                formated_data.append(PartialMatch(**self.__injector__(data=match)))
            return formated_data

    @asyncio.coroutine
    def rune_pages(self) -> typing.List[RunePage]:
        """|coro|

        Grabs all the summoners rune pages.


        Returns
        -------
        list : :class:`RunePage`
            all the rune pages belonging to the summoner


        """
        route = "runes/by-summoner/{0}".format(self.sid)
        data = yield from self.__bucket__.request("platform", route)
        if data is not None:
            response = []
            for rune_page in data['pages']:
                marks = []
                seals = []
                glyphs = []
                quints = []
                if rune_page.get("slots", False):
                    for r in rune_page['slots']:
                        rune = self.get_from_cache("runes", r.get("runeId"))
                        slot = r.get("runeSlotId")
                        if slot < 10 > 0:
                            marks.append(rune)
                        elif slot < 19 > 9:
                            seals.append(rune)
                        elif slot < 28 > 18:
                            glyphs.append(rune)
                        elif slot < 31 > 27:
                            quints.append(rune)
                    response.append(
                        RunePage(
                            **self.__injector__(data=dict(marks=marks, seals=seals, glyphs=glyphs, quintessences=quints,
                                                          name=rune_page['name'],
                                                          id=rune_page['id']))))
                else:
                    response.append(RunePage())
            return response

    @asyncio.coroutine
    def leagues(self) -> typing.Union[League, None]:
        """|coro|

        Gets all the leagues the summoner belongs to across all queue types.

        Returns
        -------
        union[:class:`League`,None]
            The league associated with the queue type if found.

        """
        endpoint = "leagues/by-summoner/{0}".format(self.sid)
        data = yield from self.__bucket__.request("league", endpoint)
        if data is not None:
            return [League(**self.__injector__(data=league)) for league in data]
        else:
            return None

    @asyncio.coroutine
    def mastery_pages(self) -> typing.List[MasteryPage]:
        """|coro|



        Returns
        -------
        list
            A List of all the summoner's :class:`MasteryPage`

        """
        route = "masteries/by-summoner/{0}".format(self.sid)
        data = yield from self.__bucket__.request("platform", route)
        if data is not None:
            return [MasteryPage(**self.__injector__(bucket=self.__bucket__, data=page)) for page in data['pages']]
