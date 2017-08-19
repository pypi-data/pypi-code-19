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
    player_stats_events = [
        x
        for x in replay.tracker_events
        if x.name == "PlayerStatsEvent" and x.player == player]

    if player_stats_events:
        workers_active_at_time = next(
            iter(
                sorted(
                    player_stats_events,
                    key=lambda x: abs((x.frame / (1.4 * replay.game_fps)) - seconds)))).workers_active_count
    else:
        workers_active_at_time = 0

    workers_in_progress_at_time = [
            event.unit
            for event
            in replay.events
            if (event.name in ["UnitBornEvent", "UnitDoneEvent"] and
                event.unit.owner == player and
                event.unit.name in ["Drone", "Probe", "SCV"] and
                event.unit.started_at / (1.4 * replay.game_fps) <= seconds and
                event.unit.died_at is not None and
                event.unit.died_at / (1.4 * replay.game_fps) > seconds and
                event.unit.finished_at is not None and
                event.unit.finished_at / (1.4 * replay.game_fps) > seconds)]

    return workers_active_at_time + len(workers_in_progress_at_time)