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
from league.enums import Queue
from league.riotDTO import RiotDto


class League(RiotDto):
    """Represents a Riot League

    Attributes
    ----------
    tier : str
        The tier of the league.

    queue : str
        The ``queueType`` the league belongs to.

    name: str
        The name of the league.

    entries: list
        List of :class:`~LeagueEntry` representing summoners in the league.

    """

    __slots__ = ('tier', 'queue', 'name', 'entries')

    def __init__(self, **kwargs):
        super(League, self).__init__(**kwargs)
        self.tier = kwargs.get('tier')
        self.queue = kwargs.get('queue')
        self.name = kwargs.get('name')
        self.entries = [LeagueEntry(**entry) for entry in kwargs.get('entries')]


class LeagueEntry(RiotDto):
    """Represents an entry in a :class:`~League`

    Attributes
    ----------
    rank: str
        The summoners rank of the league

    tier : str
        The summoner tier inside the league

    streak: bool
        Indicates if the summoner is on a hot streak

    series: :class:`Series`
        Indicates if the summoner is in a series if not this is  **None**.

    wins: int
        The amount of wins the summoner has.

    losses: int
        The amount of losses the summoner has.

    winrate: float
        The winrate of the summoner as a percentage

    total_played: int
        The total amount of games played by the summoner

    team_player_id: str
        The ID of the team or summoner.

    team_player_name: str
        The name of the team or summoner.

    inactive: bool
        Indicates if this summoner is considered inactive

    new_addition: bool
        Indicates if the summoner has recently joined the league

    league_points: int
        The amount of points the summoner has


    """

    def __init__(self, **kwargs):
        super(LeagueEntry, self).__init__(**kwargs)
        self.rank = kwargs.get('rank')
        self.streak = kwargs.get('hotStreak')
        self.tier = kwargs.get('tier')
        if kwargs.get('miniSeries') is not None:
            self.series = Series(**kwargs.get('miniSeries'))
        else:
            self.series = None
        try:
            self.queue = Queue[kwargs.get('queueType')]
        except KeyError:
            self.queue = kwargs.get('queueType')
        self.wins = kwargs.get('wins')
        self.losses = kwargs.get('losses')
        self.winrate = float(round((self.wins / (self.wins + self.losses)) * 100, 2))
        self.total_played = self.wins + self.losses
        self.veteran = kwargs.get('veteran')
        self.team_player_id = kwargs.get('playerOrTeamId')
        self.team_player_name = kwargs.get('playerOrTeamName')
        self.inactive = kwargs.get('inactive')
        self.new_addition = kwargs.get('freshBlood')
        self.league_points = kwargs.get('leaguePoints')


class Series:
    """Represents a :class:`~LeagueEntry` series progress if they are in one.

    Attributes
    ----------
    total_games: int
        The amount of games in the series.

    wins: int
        The amount of wins in the series.

    losses: int
        The amount of losses in the series.

    progress: str
        Representation of current progress in the league in the format of: ``WLN``

        * W = Win
        * L = Loss
        * N = Not played

    """

    def __init__(self, **kwargs):
        self.total_games = kwargs.get('target')
        self.wins = kwargs.get('wins')
        self.losses = kwargs.get('losses')
        self.progress = kwargs.get('progress')  # TODO format this somehow from WLNNN
