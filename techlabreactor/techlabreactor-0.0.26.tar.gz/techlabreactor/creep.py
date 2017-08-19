from sc2reader.objects import Player
from sc2reader.resources import Replay


def creep_tumours_built_before_second(second: int, player: Player, replay: Replay) -> int:
    creep_tumours = set([
        event.unit
        for event
        in replay.events
        if (event.name in ["UnitBornEvent", "UnitDoneEvent"] and
            event.unit.owner == player and
            event.unit.name == "CreepTumorBurrowed")
    ])

    creep_tumour_started_times = [int(creep_tumour.started_at / (1.4 * replay.game_fps)) for creep_tumour in creep_tumours]
    return len([time for time in creep_tumour_started_times if time < second])
