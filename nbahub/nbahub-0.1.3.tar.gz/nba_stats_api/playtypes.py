import requests
from nba_stats_api.constants import PlayTypeBase, PLAYTYPE_COLUMNS


class PlayTypeHandler:
    def __init__(self, year="2016", season_type="Reg"):
        self.year = year
        self.season_type = season_type
        self.base_url = PlayTypeBase
        self.json = None

    def _convert_playtype_key_and_val(self, key, row):
        value = row.get(key, None)

        if key == "FREQ":
            value = row['Time']
        elif key == "PTS":
            value = row['Points']
        elif key == "FG%":
            value = row['FG']
        elif key == "EFG%":
            value = row['aFG']
        elif key == "FT FREQ":
            value = row['FT']
        elif key == "TO FREQ":
            value = row['TO']
        elif key == "SF FREQ":
            value = row["SF"]
        elif key == "AND ONE FREQ":
            value = row["PlusOne"]
        elif key == "SCORE FREQ":
            value = row["Score"]
        elif key == "Percentile":
            worse_ppp = row['WorsePPP']
            better_ppp = row['BetterPPP']
            if isinstance(worse_ppp, int) and isinstance(better_ppp, int):
                denominator = row['WorsePPP'] + row['BetterPPP']
                if denominator != 0:
                    value = (row['WorsePPP'] / denominator) * 100

        return {key: value}

    def _convert_json(self, nba_json):
        new_json = {}

        for row in nba_json:
            # print(("Row: ", row))
            player_name = row['PlayerFirstName'] + " " + row['PlayerLastName']
            new_row = {'PLAYER_ID': row['PlayerIDSID'],
                       'PLAYER_NAME': player_name,
                       'TEAM_ID': row['TeamIDSID'],
                       'TEAM_ABBREVIATION': row['TeamNameAbbreviation']}
            for key in PLAYTYPE_COLUMNS:
                new_row.update(self._convert_playtype_key_and_val(key, row))
            new_json[new_row['PLAYER_ID']] = new_row

        return new_json

    def fetch_json(self, play_type):
        full_url = self.base_url.format(year=self.year,
                                        category=play_type,
                                        season_type=self.season_type)
        response = requests.get(full_url)
        self.json = self._convert_json(response.json()['results'])
