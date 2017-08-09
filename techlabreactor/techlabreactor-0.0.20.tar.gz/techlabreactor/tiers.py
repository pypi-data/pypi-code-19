from sc2reader.objects import Player
from sc2reader.resources import Replay

LAIR_MORPH_TIME = 57


def lair_started_timing(player: Player, replay: Replay) -> int:
    if player.play_race != "Zerg":
        return -1

    hatcheries = [
        event.unit
        for event
        in replay.events
        if (event.name in ["UnitDoneEvent", "UnitBornEvent"] and
            event.unit.owner == player and
            event.unit.name in ["Hatchery", "Lair", "Hive"])]

    lairs = [
        hatchery
        for hatchery
        in hatcheries
        if ("Lair" in [unit_type.name for unit_type in hatchery.type_history.values()])
    ]

    if not lairs:
        return -1

    earliest_frame = min(
        [
            min([frame for frame, unit_type in hatchery.type_history.items() if unit_type.name == "Lair"])
            for hatchery
            in lairs
        ])

    finished_second = int(earliest_frame / (1.4 * replay.game_fps))
    return finished_second - LAIR_MORPH_TIME

