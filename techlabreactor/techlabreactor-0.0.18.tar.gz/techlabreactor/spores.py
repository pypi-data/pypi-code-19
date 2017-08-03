from sc2reader.objects import Player
from sc2reader.resources import Replay


def safety_spores_timing(player: Player, replay: Replay) -> int:
    spores = [
        event.unit
        for event
        in replay.events
        if (event.name in ["UnitDoneEvent", "UnitBornEvent"] and
            event.unit.owner == player and
            event.unit.name == "Spore Crawler")]

    spore_start_times = [
        int(extractor.started_at / (replay.game_fps * 1.4))
        for extractor
        in spores]

    sorted_spore_start_times = list(sorted(spore_start_times))

    if sorted_spore_start_times:
        return sorted_spore_start_times[0]
    else:
        return -1