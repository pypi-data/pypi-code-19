from typing import List, Tuple

from sc2reader.events.tracker import PlayerStatsEvent
from sc2reader.objects import Player
from sc2reader.resources import Replay

WORKER_BUILD_DURATION = 12


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
    return worker_count_timing(44, player, replay)


def three_base_saturation_timing(player: Player, replay: Replay) -> int:
    return worker_count_timing(66, player, replay)


def worker_count_timing(worker_count: int, player: Player, replay: Replay) -> int:
    workers_active = _get_workers_active_over_time(player, replay)
    return _seconds_to_reach_worker_count(workers_active, worker_count)


def worker_supply_at(seconds: int, player: Player, replay: Replay) -> int:
    if player.play_race in ["Zerg", "Terran"]:

        worker_started_times = [
            int(event.frame / (1.4 * replay.game_fps)) - WORKER_BUILD_DURATION
            for event
            in replay.events
            if (event.name in ["UnitBornEvent", "UnitDoneEvent"] and
                event.unit.owner == player and
                event.unit.name in ["Drone", "Probe", "SCV"])]

        workers_built_before_cutoff = [time for time in worker_started_times if time < seconds]
        return len(workers_built_before_cutoff)
    else:
        return -1