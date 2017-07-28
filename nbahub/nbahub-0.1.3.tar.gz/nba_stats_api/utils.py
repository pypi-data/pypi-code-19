import requests
import re
import time
import json
from decimal import Decimal
from bs4 import BeautifulSoup
from openpyxl import Workbook
from nba_py.player import PlayerShootingSplits, PlayerList
from nba_py.league import PlayerStats
from nba_py.constants import PerMode
from nba_stats_api.playtypes import PlayTypeHandler
from nba_stats_api.constants import (BasketballReference, ALL_PLAY_TYPES,
                                     COMMON_FIELDS, PLAYTYPE_COLUMNS,
                                     VIDEO_MEASURES, VIDEO_ENDPOINT,
                                     GENERAL_STAT_TYPES)
comm = re.compile("<!--|-->")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class Player:
    def __init__(self, nba_id, name):
        self.nba_id = nba_id
        self.name = name


def get_shooting_stats(player_id, season):
    shooting_splits = PlayerShootingSplits(season=season,
                                           player_id=player_id)
    return shooting_splits.shot_5ft()[0] if len(shooting_splits.shot_5ft()) else {}


def extract_common_info(stats_dict):
    return {key: stats_dict[key] for key in COMMON_FIELDS}


def convert_dict(to_convert):
    converted = {key: to_convert[key] for key in to_convert if ("rank" not in key.lower()
                                                                and key not in COMMON_FIELDS
                                                                and key not in ["CFID", "CFPARAMS"])}
    return converted


def calc_true_shooting(player_stats_dict):
    totals = player_stats_dict['Totals']
    true_shooting_attempts = totals['FGA'] + (0.44 * totals['FTA'])
    if true_shooting_attempts != 0:
        true_shooting_percentage = Decimal(totals['PTS'] / (2 * true_shooting_attempts))
        return true_shooting_percentage
    return 0


def calc_three_point_attempt_rate(player_stats_dict):
    totals = player_stats_dict['Totals']
    fga = totals['FGA']
    if fga != 0:
        return Decimal(totals['FG3A'] / fga)
    else:
        return 0


def calc_free_throw_attempt_rate(player_stats_dict):
    totals = player_stats_dict['Totals']
    fga = totals['FGA']
    if fga != 0:
        return Decimal(totals['FTA'] / fga)
    else:
        return 0


def calc_two_pt_percentage(player_stats_dict):
    totals = player_stats_dict['Totals']
    two_pt_makes = totals['FGM'] - totals['FG3M']
    two_pt_attempts = totals['FGA'] - totals['FG3A']
    if two_pt_attempts != 0:
        return Decimal(two_pt_makes / two_pt_attempts)
    else:
        return 0


def calc_extra_shooting_stats(player_stats_dict):
    player_stats_dict['Shooting']['TS_PCT'] = calc_true_shooting(player_stats_dict)
    player_stats_dict['Shooting']['3PAr'] = calc_three_point_attempt_rate(player_stats_dict)
    player_stats_dict['Shooting']['FTr'] = calc_free_throw_attempt_rate(player_stats_dict)
    player_stats_dict['Shooting']['2PT_PCT'] = calc_two_pt_percentage(player_stats_dict)


def get_advanced_stats(bbref_id, season="2016-17"):
    url = BasketballReference.BaseURL + BasketballReference.PlayersEndpoint + bbref_id[0] + f"/{bbref_id}.html"
    response = requests.get(url)
    html = response.text
    cleaned_soup = BeautifulSoup(re.sub("<!--|-->", "", html), "html5lib")
    advanced_table = cleaned_soup.find("table", {'id': "advanced"})
    if advanced_table is not None:
        body = advanced_table.find("tbody")
        rows = body.find_all("tr")

        exclude_keys = ["yyy", "xxx", "age", "team_id", "lg_id", "pos", "g"]
        for row in rows:
            season_cell = row.find(attrs={'data-stat': "season"})
            if season_cell.text == season:
                cells = row.find_all("td")
                stats_dict = {tag.attrs['data-stat']: tag.text for tag in cells if
                              tag.attrs['data-stat'].lower() not in exclude_keys}
                return stats_dict
    else:
        return {}


def update_all_player_stats(season):
    player_stats_dict = {}

    for per_mode in [PerMode.Totals, PerMode.PerGame,
                     PerMode.Per100Possessions, PerMode.Per36]:
        print(f"Working on {per_mode}")
        player_stats = PlayerStats(season=season,
                                   per_mode=per_mode)
        time.sleep(1)
        for row in player_stats.overall():
            player_id = row['PLAYER_ID']
            new_row = convert_dict(row)
            if player_id not in player_stats_dict:
                player_stats_dict[player_id] = {'BasicInfo': extract_common_info(row)}

            player_stats_dict[player_id][per_mode] = new_row

    play_type_handler = PlayTypeHandler(year=season.split("-")[0],
                                        season_type="Reg")
    for play_type in ALL_PLAY_TYPES:
        print(f"Working on {play_type}")
        play_type_handler.fetch_json(play_type)

        for player_id in play_type_handler.json:
            player_name = play_type_handler.json[player_id]['PLAYER_NAME']
            if player_id not in player_stats_dict:
                print(f"{player_name} has entries for PlayType Statistics, but not"
                      f"traditional stats. Skipping this player.")
                continue
            player_stats_dict[player_id][play_type] = convert_dict(play_type_handler.json[player_id])

        time.sleep(1)

    player_list = PlayerList(season=season,
                             only_current=1)

    with open("bbref_id_map.json", "r") as bbref_file:
        bbref_id_map = json.loads(bbref_file.read())
        for player in player_list.info():
            player_id = player['PERSON_ID']
            player_name = player['DISPLAY_FIRST_LAST']
            print(f"Working on shooting for {player_name}")
            shooting = get_shooting_stats(player_id=player_id,
                                          season=season)
            if player_id in player_stats_dict:
                player_stats_dict[player_id]['Shooting'] = convert_dict(shooting)
                calc_extra_shooting_stats(player_stats_dict[player_id])

                bbref_id = bbref_id_map[str(player_id)]
                print(f"Working on advanced for {player_name}")
                advanced_stats = get_advanced_stats(bbref_id, season="2016-17")
                player_stats_dict[player_id]['Advanced'] = advanced_stats
            else:
                print(f"It appears {player_name} hasn't registered any statistics for this season.")

            time.sleep(1)
    return player_stats_dict
