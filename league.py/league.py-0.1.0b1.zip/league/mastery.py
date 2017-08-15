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
from league.riotDTO import RiotDto


class ChampionMastery(RiotDto):
    """Represents a :class:`Summoner`'s mastery to a :class:`champion`

    Attributes
    ----------
    chest_granted : bool
        Is chest granted for this champion or not in current season.
    level: int
        Champion level for specified player and champion combination.
    points: int
        Total number of champion points for this player and champion combination.
    tokens : int
        amount of tokens earned.
    summoner: :class:`Summoner`
        The summoner this mastery belongs to
    champion: :class:`Champion`
        The Champion of this mastery
    points_till_next: long
        Number of points needed to achieve next level. Zero if player reached maximum champion level for this champion.
    points_since_last: long
        Number of points earned since current level has been achieved. Zero if player reached maximum champion level for this champion.
    last_played : datetime.datetime
        Last time this champion was played by this player.

    """

    def __init__(self, **kwargs):
        super(ChampionMastery, self).__init__(**kwargs)
        self.chest_granted = kwargs.get('chestGranted')
        self.level = kwargs.get('championLevel')
        self.points = kwargs.get('championPoints')
        self.champion = kwargs.get('champion')
        self.summoner = kwargs.get('summoner')
        self.points_till_next = kwargs.get('championPointsUntilNextLevel')
        self.points_since_last = kwargs.get('championPointsSinceLastLevel')
        self.last_played = datetime.datetime.utcfromtimestamp(kwargs.get('lastPlayTime') / 1000)
        self.tokens = kwargs.get('tokensEarned')
