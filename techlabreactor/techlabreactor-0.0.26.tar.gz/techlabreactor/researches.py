from sc2reader.objects import Player
from sc2reader.resources import Replay

OVERLORD_SPEED_RESEARCH_ID = 'overlordspeed'
OVERLORD_SPEED_RESEARCH_DURATION = 43


def research_finished_timing(research_name: str, player: Player, replay: Replay):
    research_completed_times = [
        event.frame
        for event
        in replay.events
        if event.name == 'UpgradeCompleteEvent' and event.player == player and event.upgrade_type_name == research_name]

    if research_completed_times:
        return int(min(research_completed_times) / (1.4 * replay.game_fps))
    else:
        return -1


def overlord_speed_research_started_timing(player: Player, replay: Replay):
    completed_time = research_finished_timing(OVERLORD_SPEED_RESEARCH_ID, player, replay)

    if completed_time >= 0:
        return completed_time - OVERLORD_SPEED_RESEARCH_DURATION
    else:
        return -1
