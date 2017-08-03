from sc2reader.resources import Replay

DATE_TIME_FORMAT = "%Y-%h-%d %H:%M"


def generate_replay_summary(replay: Replay) -> dict:
    if replay.teams:
        title = " vs ".join([
            ", ".join(["{} ({})".format(player.name, player.play_race) for player in team])
            for team
            in replay.teams
        ]) + " - " + replay.map_name
    else:
        title = "Unknown players - " + replay.map_name

    return {
        "hash": replay.filehash,
        "title": title,
        "startTime": replay.start_time.strftime(DATE_TIME_FORMAT),
        "endTime": replay.end_time.strftime(DATE_TIME_FORMAT),
        "duration": "{}:{:02d}".format(*divmod(replay.real_length.seconds, 60))
    }