#! python
import json

import click

from nba_stats_api.utils import update_all_player_stats, DecimalEncoder
from nbahub.excel_handler import ExcelGenerator


@click.group()
def cli():
    pass


@cli.command()
@click.option("--season", default="2016-17", help="The season you're interested in. Must be specified in "
                                                  "YYYY-YY format. Currently defaults to 2016-17")
@click.option("--format", type=click.Choice(["excel", "json"]))
@click.option("--output", default="outputs", help="The directory you would like the output to be saved in."
                                                  " This can be specified as either a full or local path.")
def update_all(season, format, output):
    print(f"Updating all player statistics for {season}")
    # PLAYER_ID - > {'PerGame': {<stats here>}, 'Totals': <stats>, etc}
    player_stats_dict = update_all_player_stats(season)

    for player in player_stats_dict:
        this_player_stats = player_stats_dict[player]
        player_name = this_player_stats['BasicInfo']['PLAYER_NAME']

        if format == "json":
            with open(f"{output}/{player_name}.json", "w") as stat_file:
                stat_file.write(json.dumps(player_stats_dict[player],
                                           cls=DecimalEncoder))
                stat_file.close()
        elif format == "excel":
            excel_generator = ExcelGenerator(this_player_stats, season=season)
            excel_generator.generate_workbook(path=output)


def main():
    cli()
