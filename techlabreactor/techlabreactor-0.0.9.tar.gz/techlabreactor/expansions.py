from typing import List

from sc2reader.objects import Player
from sc2reader.resources import Replay


def _get_hatchery_start_times(player, replay) -> List[int]:
    hatchery_start_times = [
        int(event.unit.started_at / (replay.game_fps * 1.4))
        for event
        in replay.tracker_events
        if event.name == "UnitDoneEvent" and event.unit.owner == player and event.unit.name == "Hatchery"]

    return list(sorted(hatchery_start_times))


def natural_expansion_timing(player: Player, replay: Replay) -> int:
    hatchery_start_times = _get_hatchery_start_times(player, replay)
    return hatchery_start_times[0] if hatchery_start_times else -1


def third_expansion_timing(player: Player, replay: Replay) -> int:
    hatchery_start_times = _get_hatchery_start_times(player, replay)
    return hatchery_start_times[1] if len(hatchery_start_times) >= 2 else -1
