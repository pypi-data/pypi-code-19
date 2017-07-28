

class BasketballReference:
    BaseURL = "https://www.basketball-reference.com"
    PlayersEndpoint = "/players/"

# Note that {year} refers to the pre-New Year's portion of the season in question.
# For example, if you want 2016-17 stats, year = 2016.
PlayTypeBase = ("http://stats-prod.nba.com/wp-json/statscms/v1/synergy/player/?"
        "category={category}&limit=500&names=offensive&q=2501056&season={year}&"
        "seasonType={season_type}")

GENERAL_STAT_TYPES = ["Totals", "PerGame", "Per100Possessions", "Per36", "Advanced", "Shooting"]

Transition = "Transition"
Isolation = "Isolation"
PnRBallHandler = "PRBallHandler"
PnRRollMan = "PRRollman"
PostUp = "Postup"
SpotUp = "Spotup"
HandOff = "Handoff"
Cut = "Cut"
OffScreen = "OffScreen"
PutBacks = "OffRebound"
Misc = "Misc"

ALL_PLAY_TYPES = [Transition, Isolation, PnRBallHandler, PnRRollMan,
                  PostUp, SpotUp, HandOff, Cut, OffScreen, PutBacks, Misc]

COMMON_FIELDS = ["PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "TEAM_ABBREVIATION", "AGE", "GP", "W", "L", "W_PCT"]
PLAYTYPE_COLUMNS = ['Poss', 'FREQ', 'PPP', 'PTS', 'FGM', 'FGA', 'FG%', 'EFG%', 'FT FREQ', 'TO FREQ', 'SF FREQ',
                    'AND ONE FREQ', 'SCORE FREQ', 'Percentile']

VIDEO_ENDPOINT = ("http://stats.nba.com/events/#!/?flag=3&CFID=&CFPARAMS=&PlayerID={player_id}&TeamID=&GameID=&Context"
                  "Measure={measure}&Season={season}&SeasonType={season_type}&LeagueID=00&PerMode=PerGame&GameSegment="
                  "&Period=0&PlayerPosition=&StarterBench=&PlayerExperience=&OpponentTeamID=0&VsConference=&VsDivision="
                  "&Outcome=&Location=&SeasonSegment=&Month=0&LastNGames=0&PlusMinus=N&PaceAdjust=N&Rank=N&GameScope=&D"
                  "ateFrom=&DateTo=&ShotClockRange=&Conference=&Division=&PORound=0&DraftYear=&DraftPick=&College=&Coun"
                  "try=&Height=&Weight=&MeasureType=Base&section=players&sct=hex")
VIDEO_MEASURES = {"FGM": "Field goal Makes",
                  "FGA": "Field Goal Attempts",
                  "FG3M": "Three-Point Makes",
                  "FG3A": "Three-Point Attempts",
                  "OREB": "Offensive Rebounds",
                  "DREB": "Defensive Rebounds",
                  "REB": "Rebounds",
                  "AST": "Assists",
                  "TOV": "Turnovers",
                  "STL": "Steals",
                  "BLK": "Blocks",
                  "PF": "Fouls"}
