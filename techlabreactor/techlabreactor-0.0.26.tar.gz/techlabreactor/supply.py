from typing import List, Tuple

from sc2reader.events import PlayerStatsEvent
from sc2reader.objects import Player
from sc2reader.resources import Replay

from techlabreactor.gametime import frame_to_second


def get_supply_blocks_till_time_for_player(second: int, player: Player, replay: Replay) -> List[Tuple[float, bool]]:
    player_stats_events = [
        event
        for event
        in replay.events
        if (isinstance(event, PlayerStatsEvent) and
            event.player == player and
            frame_to_second(event.frame) <= second)]

    result = [(0.0, False)]
    for event in player_stats_events:
        result.append((frame_to_second(event.frame), event.food_used >= event.food_made))

    result.append((second, result[-1][1]))

    return result

