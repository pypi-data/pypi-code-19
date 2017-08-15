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

"""
Some code taken from:
https://github.com/meraki-analytics/cassiopeia/blob/master/cassiopeia/type/core/common.py
"""

from enum import Enum


class Regions(Enum):
    """Represents all valid legal regions for the api

    Attributes
    ----------
    br
    eune
    euw
    jp
    kr
    lan
    las
    na
    oce
    tr
    ru
    pbe

    """
    br = "br1"
    eune = "eun1"
    euw = "euw1"
    jp = "jp1"
    kr = "kr"
    lan = "la1"
    las = "la2"
    na = 'na1'
    oce = "oc1"
    tr = "tr1"
    ru = "ru"
    pbe = "pbe1"


class DataDragon(Enum):
    __base_url__ = "http://ddragon.leagueoflegends.com/cdn/"
    __data_version__ = "6.24.1"
    profile_icons = "{0}/img/profileicon/{1}"
    champion_splash = "img/champion/splash/{0}_{1}.jpg"
    champion_loading = "img/champion/loading/{0}_{1}.jpg"
    champion_square = "{0}/img/champion/{1}"
    passive = "{0}/img/passive/{0}"
    champion_spell = "{0}/img/spell/{0}"
    summoner_spell = "{0}/img/spell/Summoner{0}"
    item = "{0}/img/item/{1}"
    summoner_mastery = "{0}/img/mastery/{1}"
    rune = "{0}/img/rune/{1}"
    sprite = "{0}/img/sprite/{1}"
    minimap = "6.8.1/img/map/{1}"
    score_bored = "5.5.1/img/ui/{0}"


class RouteVersions(Enum):
    """Represents current route versions

    used to make future route versions easier to manage throughout code

    """
    champion_mastery = "v3"
    platform = "v3"
    league = "v3"
    static_data = "v3"
    status = "v3"
    masteries = "v3"
    match = "v3"
    runes = "v3"
    spectator = "v3"
    summoner = "v3"
    tournament_stub = "v3"
    tournament = 'v3'


class Queue(Enum):
    """Represnts all possible queue types

    Attributes
    ----------
    custom
    normal_blind_threes
    normal_blind_fives
    normal_draft_fives
    ranked_solo
    ranked_premade_fives
    ranked_premade_threes
    ranked_threes
    ranked_fives
    dominion_blind
    dominion_draft
    bot_dominion
    bot_fives
    bot_intro_fives
    bot_beginner_fives
    bot_intermediate_fives
    bot_threes
    team_builder
    aram
    one_for_all
    showdown_solo
    showdown_duo
    hexakill_summoners_rift
    urf
    one_for_all_mirror
    bot_urf
    doom_bots_1
    doom_bots_2
    doom_bots_5
    ascension
    hexakill_twisted_treeline
    butchers_bridge
    poro_king
    nemesis_draft
    black_market
    nexus_siege
    definitely_not_dominion
    random_urf
    dynamic_queue
    ranked_dynamic_queue
    ranked_solo_queue
    flex
    flex_threes


    """
    custom = "CUSTOM"
    normal_blind_threes = "NORMAL_3x3"
    normal_blind_fives = "NORMAL_5x5_BLIND"
    normal_draft_fives = "NORMAL_5x5_DRAFT"
    ranked_solo = "RANKED_SOLO_5x5"
    ranked_premade_fives = "RANKED_PREMADE_5x5"
    ranked_premade_threes = "RANKED_PREMADE_3x3"
    ranked_threes = "RANKED_TEAM_3x3"
    ranked_fives = "RANKED_TEAM_5x5"
    dominion_blind = "ODIN_5x5_BLIND"
    dominion_draft = "ODIN_5x5_DRAFT"
    bot_dominion = "BOT_ODIN_5x5"
    bot_fives = "BOT_5x5"
    bot_intro_fives = "BOT_5x5_INTRO"
    bot_beginner_fives = "BOT_5x5_BEGINNER"
    bot_intermediate_fives = "BOT_5x5_INTERMEDIATE"
    bot_threes = "BOT_TT_3x3"
    team_builder = "GROUP_FINDER_5x5"
    aram = "ARAM_5x5"
    one_for_all = "ONEFORALL_5x5"
    showdown_solo = "FIRSTBLOOD_1x1"
    showdown_duo = "FIRSTBLOOD_2x2"
    hexakill_summoners_rift = "SR_6x6"
    urf = "URF_5x5"
    one_for_all_mirror = "ONEFORALL_MIRRORMODE_5x5"
    bot_urf = "BOT_URF_5x5"
    doom_bots_1 = "NIGHTMARE_BOT_5x5_RANK1"
    doom_bots_2 = "NIGHTMARE_BOT_5x5_RANK2"
    doom_bots_5 = "NIGHTMARE_BOT_5x5_RANK5"
    ascension = "ASCENSION_5x5"
    hexakill_twisted_treeline = "HEXAKILL"
    butchers_bridge = "BILGEWATER_ARAM_5x5"
    poro_king = "KING_PORO_5x5"
    nemesis_draft = "COUNTER_PICK"
    black_market = "BILGEWATER_5x5"
    nexus_siege = "SIEGE"
    definitely_not_dominion = "DEFINITELY_NOT_DOMINION_5x5"
    random_urf = "ARURF_5X5"
    dynamic_queue = "TEAM_BUILDER_DRAFT_UNRANKED_5x5"
    ranked_dynamic_queue = "TEAM_BUILDER_DRAFT_RANKED_5x5"
    ranked_solo_queue = "TEAM_BUILDER_RANKED_SOLO"
    flex = "RANKED_FLEX_SR"
    flex_threes = "RANKED_FLEX_TT"


def for_id(id_):
    try:
        return Queue.by_id[id_]
    except:
        return None


Queue.by_id = {
    0: Queue.custom,
    8: Queue.normal_blind_threes,
    2: Queue.normal_blind_fives,
    14: Queue.normal_draft_fives,
    4: Queue.ranked_solo,
    6: Queue.ranked_premade_fives,
    9: Queue.flex_threes,
    41: Queue.ranked_threes,
    42: Queue.ranked_fives,
    16: Queue.dominion_blind,
    17: Queue.dominion_draft,
    25: Queue.bot_dominion,
    7: Queue.bot_fives,
    31: Queue.bot_intro_fives,
    32: Queue.bot_beginner_fives,
    33: Queue.bot_intermediate_fives,
    52: Queue.bot_threes,
    61: Queue.team_builder,
    65: Queue.aram,
    70: Queue.one_for_all,
    72: Queue.showdown_solo,
    73: Queue.showdown_duo,
    75: Queue.hexakill_summoners_rift,
    76: Queue.urf,
    78: Queue.one_for_all_mirror,
    83: Queue.bot_urf,
    91: Queue.doom_bots_1,
    92: Queue.doom_bots_2,
    93: Queue.doom_bots_5,
    96: Queue.ascension,
    98: Queue.hexakill_twisted_treeline,
    100: Queue.butchers_bridge,
    300: Queue.poro_king,
    310: Queue.nemesis_draft,
    313: Queue.black_market,
    315: Queue.nexus_siege,
    317: Queue.definitely_not_dominion,
    318: Queue.random_urf,
    400: Queue.dynamic_queue,
    410: Queue.ranked_dynamic_queue,
    420: Queue.ranked_solo_queue,
    440: Queue.flex
}
ranked_queues = {Queue.ranked_solo, Queue.ranked_threes, Queue.ranked_fives, Queue.ranked_dynamic_queue, Queue.flex,
                 Queue.flex_threes, Queue.ranked_solo_queue}


class Tier(Enum):
    challenger = "CHALLENGER"
    master = "MASTER"
    diamond = "DIAMOND"
    platinum = "PLATINUM"
    gold = "GOLD"
    silver = "SILVER"
    bronze = "BRONZE"
    unranked = "UNRANKED"


class Division(Enum):
    one = "I"
    two = "II"
    three = "III"
    four = "IV"
    five = "V"
