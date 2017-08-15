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


class LiveMatch(RiotDto):
    """Represents a live Match

    Attributes
    ----------
    id : long
        The ID of the game
    start_date : datetime
        The datatime of the match start
    platformID: str
        The ID of the platform on which the game is being played
    mode : str
        The Match Mode
    mapId : long
        The ID of the map
    match_type :  str
        The type of game being played
    bans : list
        Banned champion information
        dict containing:
        * pickturn : int
        * champion : long
        * teamid : long
    live_key : str
        Key used to decrypt the spectator grid game data for playback
    participants : list[:class:`LiveMatchParticipant`]
        The participant information
    length : long
        The amount of time in seconds that has passed since the game started

    """

    def __init__(self, **kwargs):
        super(LiveMatch, self).__init__(**kwargs)

        self.id = kwargs.get('gameId')
        self.start_date = datetime.datetime.utcfromtimestamp(kwargs.get('gameStartTime') / 1000)
        self.platformID = kwargs.get('platformId')
        self.mode = kwargs.get('gameMode')
        self.mapId = kwargs.get('mapId')
        self.match_type = kwargs.get('gameType')
        self.bans = [{"pickturn": turn['pickTurn'], "champion": kwargs['cache']['champions'][turn['championId']],
                      "teamid": turn['teamId']} for turn in kwargs.get('bannedChampions')]
        self.live_key = kwargs['observers']['encryptionKey']
        self.participants = [LiveMatchParticipant(champion=kwargs['cache']['champions'][data['championId']], **data) for
                             data in kwargs.get('participants')]
        self.length = kwargs.get('gameLength')

    def get_teams(self):
        """returns a dict of all teams with the members of the team.

        Returns
        -------
        dict
            A mapping of int(teamid): list[:class:`LiveMatchParticipant`]

        """
        teams = {}
        for player in self.participants:
            if player.teamId not in teams.keys():
                teams.update({player.teamId: []})
            else:
                teams[player.teamId].append(player)


class LiveMatchParticipant:
    """Represents a participant to a :class:`LiveMatch`

    Attributes
    ----------
    icon_id : long
        The ID of the profile icon used by this participant
    cid : long
        The ID of the champion played by this participant
    name : str
        The summoner name of this participant
    runes : list
        The runes used by this participant. Tuple pair (count,runeId)
    bot : bool
        Flag indicating whether or not this participant is a bot
    teamId : long
        The team ID of this participant, indicating the participant's team
    summoner_spells : tuple
        summoner spell IDs
    masteries : list
        The masteries used by this participant.
    sid: long
        The summoner ID of this participant


    """

    def __init__(self, **kwargs):
        self.icon_id = kwargs.get('profileIconId')
        self.cid = kwargs.get('championID')
        self.name = kwargs.get("summonerName")
        self.runes = kwargs.get('runes')
        self.bot = kwargs.get('bot')
        self.teamId = kwargs.get('teamId')
        self.summoner_spells = (kwargs.get('spell1Id'), kwargs.get('spell2Id'))
        self.masteries = kwargs.get('masteries')
        self.sid = kwargs.get('summonerId')
