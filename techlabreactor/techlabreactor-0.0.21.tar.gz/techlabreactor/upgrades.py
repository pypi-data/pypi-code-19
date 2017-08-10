from sc2reader.events import CommandEvent
from sc2reader.objects import Player
from sc2reader.resources import Replay

GENERIC_UPGRADE_ABILITY_NAMES = [
    "ResearchZergMeleeWeaponsLevel1",
    "ResearchZergGroundArmorsLevel1"
]


def first_upgrade_started_timing(player: Player, replay: Replay) -> int:
    upgrade_ability_event_timings = [
        int(event.frame / (replay.game_fps * 1.4))
        for event
        in replay.game_events
        if (isinstance(event, CommandEvent) and
            event.player == player and
            event.ability_name in GENERIC_UPGRADE_ABILITY_NAMES)
    ]

    return next(iter(sorted(upgrade_ability_event_timings)), -1)