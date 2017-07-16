from typing import List, Tuple

from sc2reader.events.tracker import PlayerStatsEvent
from sc2reader.objects import Player
from sc2reader.resources import Replay


def _get_workers_active_over_time(player: Player, replay: Replay) -> List[Tuple[float, int]]:
    times = [
        (event.frame / (replay.game_fps * 1.4), event.workers_active_count)
        for event
        in replay.tracker_events
        if isinstance(event, PlayerStatsEvent) and event.player == player]

    return list(sorted(times, key=lambda x: x[0]))


def _seconds_to_reach_worker_count(workers_active: List[Tuple[float, int]], worker_count: int):
    return next((int(seconds) for seconds, workers in workers_active if workers >= worker_count), -1)


def two_base_saturation_timing(player: Player, replay: Replay) -> int:
    workers_active = _get_workers_active_over_time(player, replay)
    return _seconds_to_reach_worker_count(workers_active, 44)


def three_base_saturation_timing(player: Player, replay: Replay) -> int:
    workers_active = _get_workers_active_over_time(player, replay)
    return _seconds_to_reach_worker_count(workers_active, 66)