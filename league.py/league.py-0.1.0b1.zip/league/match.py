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
from collections import namedtuple
import datetime
from league.enums import Regions, Queue, for_id
import typing
from league.riotDTO import RiotDto


class Match(RiotDto):
    """Represents a League Match

    Attributes
    ----------
    seasonID: int
        The ID of the season when the match was recorded.
    queueID: int
        The ID of the queue-type the match is for.
    matchID: int
        The Match ID.
    players: list[:class:`Player`]
        A list of :class:`Player`. Can be empty if not ranked.
    version: str
        The Patch the match was played on.
    platform: str
        The region the match was played on.
    mode: str
        The match-type of the match.
    mapid: int
        The ID of the map the match is played on.
    matchtype: str
        The match-type of the match.
    teams: list
        List of :class:`TeamStats`
    participants: list[:class:`Participant`]
        List of :class:`Participant`
    duration: long
        The duration of the match in seconds
    date: datetime.datetime
        The datetime of when the match was played

    """

    def __init__(self, **kwargs):
        super(Match, self).__init__(**kwargs)
        self.__cache__ = kwargs.get('cache')
        self.seasonID = kwargs.get('seasonId')
        self.queueID = kwargs.get('queueId')
        self.matchID = kwargs.get('gameId')
        if kwargs['participantIdentities'][0].get("player"):
            self.players = [Player(participantID=player['participantId'], **player['player']) for player in
                            kwargs.get('participantIdentities')]
        else:
            self.players = None
        self.version = kwargs.get('gameVersion')
        self.platform = kwargs.get('platformId')
        self.mode = kwargs.get('gameMode')
        self.mapid = kwargs.get('mapId')
        self.matchtype = kwargs.get('gameType')
        self.teams = [TeamStats(cache=kwargs.get('cache'), **team) for team in kwargs.get('teams')]
        self.participants = [Participant(champion=self.get_from_cache("champions", player['championId']), **player) for
                             player in kwargs.get('participants')]
        self.duration = kwargs.get('gameDuration')
        self.date = datetime.datetime.utcfromtimestamp((kwargs.get('gameCreation') / 1000))

    def get_participant(self, summoner) -> typing.Union["Participant", None]:
        """

        A helper method to easily return a summoner's participant obj from a Match

        Parameters
        ----------
        summoner :  :class:`Summoner`
            The summoner to find

        Returns
        -------
        :class:`Participant`


        """
        if self.players is not None:
            for player in self.players:
                if player.sid == summoner.sid:
                    for part in self.participants:
                        if part.pid == player.participant_id:
                            return part
        else:
            return None


class Player:
    """
    Represents a summoner of a :class:`Match`

    Attributes
    ----------
    sid: int
        Summoner ID.

    name: str
        Summoner name.

    icon: int
        ID of the summoner icon associated with the summoner.

    region: str
        The :class:`Region` of the summoner.

    account_id: int
        Account ID.

    """

    def __init__(self, **kwargs):
        self.sid = kwargs.get('summonerId')
        self.name = kwargs.get('summonerName')
        self.icon = kwargs.get('profileIcon')
        self.region = kwargs.get('platformId')
        self.account_id = kwargs.get('accountId')
        self.participant_id = kwargs.get('participantID')


class TeamStats(RiotDto):
    """ Represents a Team's stats to a :class:`Match`

    Attributes
    ----------
    result : bool
        Indicating if the team won True = win False = lose
    first_dragon : bool
        Indicates if the team got the first dragon.
    first_inhibitor : bool
        Indicates if the the got the first inhibitor.
    first_herald : bool
        Indicates if the team got the rift herald.
    first_baron : bool
        Indicates if the team got the first baron.
    first_blood : bool
        Indicates if the team got the first blood.
    first_tower : bool
        Indicates if the team got the first tower.
    bans: list[:class:`namedtuple`]
        list of :class:`namedtuple` pair of (turn/champion).
    barons : int
        Amount of barons taken by the team.
    dragons : int
        Amount of dragons taken by the team.
    inhibitor_kills : int
        Amount of inhibitors killed by the team
    tower_kills : int
        Amount of towers killed by the team
    """

    def __init__(self, **kwargs):
        super(TeamStats, self).__init__(**kwargs)
        _bans = namedtuple("_bans", "turn champion")
        self.first_dragon = kwargs.get('firstDragon')
        self.first_inhibitor = kwargs.get('firstinhibitor')
        self.first_herald = kwargs.get('firstRiftHerald')
        self.first_baron = kwargs.get('firstBaron')
        self.first_blood = kwargs.get('firstBlood')
        self.first_tower = kwargs.get('firstTower')
        self.bans = [_bans(turn=turn['pickTurn'], champion=self.get_from_cache("champions", turn['championId'])) for
                     turn in
                     kwargs.get('bans')]
        self.barons = kwargs.get('baronKills')
        self.dragons = kwargs.get('dragonKills')
        self.inhibitor_kills = kwargs.get('inhibitorKills')
        self.tower_kills = kwargs.get('towerKills')
        self.result = True if kwargs.get('win').lower() == "win" else False


class Participant:
    """Represents a summoner of a :class:`Match`

    Attributes
    ----------

    stats : :class:`ParticipantStats`
        The summoners stats of the match
    pid : int
        The participant ID in relation to the match
    runes: :class:`namedtuple`
        namedtuple pair in the format of (runeid,rank)
    timeline : :class:`ParticipantTimeLine`
        The summoners timeline of the match
    team_id : int
        The team the participant belongs to
    summoner_spells : :class:`namedtuple`
        spell IDs namedtuple pair in the format of (**D,F**)
        ```spells.d = "flash"
        spells.f = "ghost"```
    masteries : list[:class:`namedtuple`]
        participant mastery data in a namedtuple pair in the format of (mastery_id,rank)
    highest_season_rank : str
        The highest rank the participant has achieved in the current season.
    champion : :class:`Champion`
        The participants Champion
    """

    def __init__(self, **kwargs):
        summoner_spells = namedtuple("summoner_spells", "spell1Id spell2Id")
        runes = namedtuple("runes", "runeId rank")
        masteries = namedtuple("masteries", "masteryId rank")
        self.stats = ParticipantStats(**kwargs.get('stats')) if kwargs.get('stats') else None
        self.pid = kwargs.get('participantId')
        self.runes = runes(runeId=kwargs.get('runeId'), rank=kwargs.get('rank'))
        self.timeline = ParticipantTimeLine(**kwargs.get("timeline"))
        self.team_id = kwargs.get('teamId')
        self.summoner_spells = summoner_spells(kwargs.get('spell1Id'), kwargs.get('spell2Id'))
        self.masteries = [masteries(mastery['masteryId'], mastery['rank']) for mastery in kwargs.get('masteries')]
        self.highest_season_rank = kwargs.get('highestAchievedSeasonTier')
        self.champion = kwargs.get('champion')


class ParticipantStats:
    """Represents a participant's stats in a match

    Contains **a lot** of information for the sake of completion, a lot of these could be **0** or **None** depending
    on the match-type returned.

    Attributes
    ----------
    damage_done : dict
        A Dictonary containing damage done stats:
        * total : long
        * total_champions : long
        * true : long
        * true_champions : long
        * physical: long
        * physical_champions: int
        * magic : long
        * magic_champions : long
        * turrets : long
        * objectives : long

    damage_taken : dict
        A Dictonary containing damage taken stats:
        * total : long
        * true_ : long
        * physical: long
        * magic : long
        * mitigated : long

    minions_killed_team_jungle : int
        Amount of minions killed in the team jungle.
    minions_killed_enemy_junge : int
        Amount of minions killed in the enemy jungle.

    ministats : dict
        a dictionary containing:
        * kills : int
        * deaths : int
        * assists : int
        * cs : int

    win: bool
        Indicates if the participant won the match.
    largest_crit: int
        Record of the highest critical attack achieved during the match.

    largest_killing_spree : int
        Highest amount of kills before dying.
    inventory: list[**itemID**]
        List of item id's in order of inventory. Last entry is the token.
    first_blood_assist : bool
        Indicates if the champion assisted with first blood.
    first_blood_kill : bool
        Indicates if the champion got first blood.
    vision_score : int
        Score related to vision.
    vision_wards_bought : int
        Amount of vision wards bought.
    sight_wards_bought : int
        Amount of sight wards bought.
    turret_kills : int
        Amount of turrets destroyed.
    champ_level : int
        Highest champion level achieved.
    first_inhibitor_kill : bool
        Indicates if the champion destroyed the first inhibitor.
    first_inhibitor_assist : bool
        Indicates if the champion assisted with the first inhibitor kill
    inhibitor_kills : int
        Amount of inhibitors destroyed by the champion
    gold_earned : int
        Amount of gold earned.
    multikills : dict
        A dictionary containing:
        * double
        * triple
        * quadra
        * penta
        :class:`int` amount of multikills obtained by the champion.
    largest_multikill : int
        The largest multikill achieved.
    sprees:
        Amount of killing sprees obtained throughout the match.
    amount_healed : int
        Amount healed during the match.
    total_units_healed : int
        Amount of units healed throughout the match.
    time_cc_others : long
        Amount of time spent crowd-controlling others.
    rank :  int
        The score Riot gives the champion.
    """

    def __init__(self, **kwargs):
        self.damage_done = {
            "total": kwargs.get('totalDamageDealt', 0),
            "total_champions": kwargs.get('totalDamageDealtToChampions', 0),
            "true": kwargs.get('trueDamageDealt', 0),
            "true_champions": kwargs.get('trueDamageDealtToChampions', 0),
            "physical": kwargs.get('physicalDamageDealt', 0),
            "physical_champions": kwargs.get('physicalDamageDealtToChampions', 0),
            "magic": kwargs.get('magicDamageDealt', 0),
            "magic_champions": kwargs.get('magicDamageDealtToChampions', 0),
            "turrets": kwargs.get("damageDealtToTurrets", 0),
            "objectives": kwargs.get('damageDealtToObjectives', 0)
        }
        self.damage_taken = {
            "total": kwargs.get('totalDamageTaken', 0),
            "true": kwargs.get('trueDamageTaken', 0),
            "physical": kwargs.get('physicalDamageTaken', 0),
            "magic": kwargs.get('magicalDamageTaken', 0),
            "mitigated": kwargs.get("damageSelfMitigated", 0)
        }
        self.minions_killed_team_jungle = kwargs.get('neutralMinionsKilledTeamJungle', 0)
        self.minions_killed_enemy_jungle = kwargs.get('neutralMinionsKilledEnemyJungle', 0)
        self.ministats = {
            "kills": kwargs.get('kills', 0),
            "deaths": kwargs.get('deaths', 0),
            "assists": kwargs.get('assists', 0),
            "creepscore": kwargs.get('totalMinionsKilled', 0),
        }
        self.win = kwargs.get('win', False)
        self.largest_crit = kwargs.get('largestCriticalStrike', 0)
        self.largest_killing_spree = kwargs.get('largestKillingSpree', 0)
        self.inventory = [
            kwargs.get('item0'),
            kwargs.get('item1'),
            kwargs.get('item2'),
            kwargs.get('item3'),
            kwargs.get('item4'),
            kwargs.get('item5'),
            kwargs.get('item6')
        ]
        self.first_blood_assist = kwargs.get("firstBloodAssist", False)
        self.first_blood_kill = kwargs.get('firstBloodKill', False)
        self.vision_score = kwargs.get('visionScore', 0)
        self.vision_wards_bought = kwargs.get('visionWardsBoughtInGame', 0)
        self.sight_wards_bought = kwargs.get('sightWardsBoughtInGame', 0)
        self.turret_kills = kwargs.get('turretKills', 0)
        self.champion_level = kwargs.get('champLevel', 0)
        self.first_inhibitor_kill = kwargs.get('firstInhibitorKill', False)
        self.first_inhibitor_assist = kwargs.get("firstInhibitorAssist", False)
        self.inhibitor_kills = kwargs.get('inhibitorKills', 0)
        self.gold_earned = kwargs.get('goldEarned', 0)
        self.mutilkills = {
            "double": kwargs.get("doubleKills", 0),
            "triple": kwargs.get('tripleKills', 0),
            "quadra": kwargs.get('quadraKills', 0),
            "penta": kwargs.get("pentaKills", 0),
        }
        self.sprees = kwargs.get('killingSprees', 0)
        self.amount_healed = kwargs.get('totalHeal', 0)
        self.units_healed = kwargs.get("totalUnitsHealed", 0)
        self.time_cc_others = kwargs.get("timeCCingOthers", 0)
        self.rank = kwargs.get('totalScoreRank')


class ParticipantTimeLine:
    """Represents the time-line of a participant

    Attributes
    ----------
    lane : str
        the lane the participant played in
    id : int
        participant ID
    role:
        The role the participant is seen as, could be None.
    cs_per_min : dict
        A dictionary consisting of creep score earned per minute.
    cs_diff_min : dict
        A dictionary consisting of creep score differentials.
    gold_per_min : dict
        A dictionary consisting of gold per minute earned.
    exp_diff_min : dict
        A dictionary consisting of experience differentials.
    exp_per_min : dict
        A dictionary consisting of experience earned per minute.

    damage_taken_diff : dict
        A dictionary consisting of damage taken differentials.
    damage_taken_per_min : dict
        A dictionary consisting of damage taken per minute.


    """

    def __init__(self, **kwargs):
        self.lane = kwargs.get('lane')
        self.id = kwargs.get('participantId', 0)
        self.role = kwargs.get('role')
        self.cs_per_min = kwargs.get('creepsPerMinDeltas')
        self.cs_diff_min = kwargs.get('csDiffPerMinDeltas')
        self.gold_per_min = kwargs.get('goldPerMinDeltas')
        self.exp_diff_min = kwargs.get('xpDiffPerMinDeltas')
        self.exp_per_min = kwargs.get('xpPerMinDeltas')
        self.damage_taken_diff = kwargs.get("damageTakenDiffPerMinDeltas")
        self.damage_taken_per_min = kwargs.get("damageTakenPerMinDeltas")


class PartialMatch(RiotDto):
    """
    Represents a partial match data.

    Attributes
    ----------
    lane: str
        represents the lane that was played as
    match_id : long
        the ID of the match, can be used to lookup the full details of the match
    champion: :class:`Champion`
        The champion played
    platform : str
        The regional platform the match was conducted on
    season : int
        The ID of the season the match belongs to.
    queue : :class:`Queue`
        the queue type of the match
    role : str
        The role of the docs

    """

    def __init__(self, **kwargs):
        super(PartialMatch, self).__init__(**kwargs)
        self.lane = kwargs.get('lane')
        self.match_id = kwargs.get('gameId')
        self.champion = kwargs.get('champion')
        self.platform = kwargs.get('platformId')
        self.season = kwargs.get('season')
        self.queue = for_id(kwargs.get('queue'))
        self.role = kwargs.get('role')
        self.date = datetime.datetime.utcfromtimestamp((kwargs.get('timestamp') / 1000))
