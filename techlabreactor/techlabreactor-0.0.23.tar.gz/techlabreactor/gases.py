from sc2reader.objects import Player
from sc2reader.resources import Replay


def second_gas_timing(player: Player, replay: Replay) -> int:
    extractors = [
        event.unit
        for event
        in replay.events
        if (event.name in ["UnitDoneEvent", "UnitBornEvent"] and
            event.unit.owner == player and
            event.unit.name == "Extractor")]

    extractor_start_times = [
        int(extractor.started_at / (replay.game_fps * 1.4))
        for extractor
        in extractors]

    sorted_extractor_start_times = list(sorted(extractor_start_times))

    if len(sorted_extractor_start_times) >= 2:
        return sorted_extractor_start_times[1]
    else:
        return -1