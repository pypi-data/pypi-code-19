import itertools
from collections import OrderedDict
from typing import Dict, Tuple, List, Set, Union

from sc2reader.data import Unit, UnitType
from sc2reader.events import UnitBornEvent, UnitDoneEvent
from sc2reader.objects import Player
from sc2reader.resources import Replay

from .gametime import frame_to_second

ORBITAL_TRANSFORMATION_DURATION = 25
PLANETARY_FORTRESS_TRANSFORMATION_DURATION = 36


def _get_production_duration(unit_type: UnitType, replay: Replay) -> float:
    if "Reactor" in unit_type.name:
        build_time = 50
    elif "TechLab" in unit_type.name:
        build_time = 25
    elif unit_type.name == "Cyclone":
        build_time = 45
    elif unit_type.name == "Liberator":
        build_time = 60
    elif unit_type.name == "BattleHellion":
        build_time = 30
    else:
        matching_build_times = [
            ability.build_time
            for ability
            in replay.datapack.abilities.values()
            if ability.is_build and ability.build_unit == unit_type]

        if not matching_build_times:
            raise Exception

        build_time = matching_build_times[0]

    return build_time / 1.44


def _get_unit_type(unit: Unit) -> UnitType:
    return next(iter(unit.type_history.values()))


def _get_structure_type(unit_type: UnitType) -> str:
    unit_name = unit_type.name

    if "Barracks" in unit_name:
        return "Barracks"

    if "Factory" in unit_name:
        return "Factory"

    if "Starport" in unit_name:
        return "Starport"

    if unit_name == "SCV":
        return "CommandCenter"

    if unit_name in ["Marine", "Marauder", "Reaper", "Ghost"]:
        return "Barracks"

    if unit_name in ["Hellion", "BattleHellion", "Cyclone", "SiegeTank", "Thor", "WidowMine"]:
        return "Factory"

    if unit_name in ["Medivac", "Viking", "Liberator", "Raven", "Banshee", "Battlecruiser"]:
        return "Starport"

    return "Unknown"


def _order_by_tech_tier(args):
    structure_type = args[0]
    return ["CommandCenter", "Barracks", "Factory", "Starport", "Unknown"].index(structure_type)


def _extract_production_structures(unit_events: List[Union[UnitBornEvent, UnitDoneEvent]]) -> Set[Unit]:
    return set(
        event.unit
        for event
        in unit_events
        if _get_unit_type(event.unit).name in [
            "CommandCenter",
            "Barracks",
            "Factory",
            "Starport"
        ])


def _extract_produced_units(unit_events: List[Union[UnitBornEvent, UnitDoneEvent]]) -> Set[Unit]:
    return set(
        event.unit
        for event
        in unit_events
        if (event.unit.finished_at > 0 and
            not event.unit.hallucinated and
            event.unit.name != "MULE" and
            ("TechLab" in event.unit.name or
             "Reactor" in event.unit.name or
             "Liberator" in event.unit.name or
             "Cyclone" in event.unit.name or
             event.unit.is_army or
             event.unit.is_worker)))


def _terran_production_used_and_capacity_events(
        replay: Replay,
        produced_units: Set[Unit],
        production_structures: Set[Unit],
        reactors: Set[Unit],
        limit_seconds: int = 0) -> Tuple[List[Tuple[float, int]], List[Tuple[float, int]]]:

    production_events = list(itertools.chain.from_iterable(
        filter(
            lambda x: x[1] <= limit_seconds,
            [
                (_get_structure_type(_get_unit_type(unit)),
                 frame_to_second(unit.finished_at) - _get_production_duration(_get_unit_type(unit), replay),
                 1),
                (_get_structure_type(_get_unit_type(unit)),
                 frame_to_second(unit.finished_at),
                 -1)])
        for unit
        in produced_units))
    production_events.sort(key=lambda x: x[1])

    production_capacity_events = []
    for unit in production_structures:
        second_finished_at = frame_to_second(unit.finished_at)
        if second_finished_at <= limit_seconds:
            production_capacity_events.append((_get_unit_type(unit).name, second_finished_at, 1))

        if unit.died_at is not None:
            second_died_at = frame_to_second(unit.died_at)
            if second_died_at <= limit_seconds:
                production_capacity_events.append((_get_unit_type(unit).name, second_died_at, -1))

        was_flying = False
        for frame, unit_type in unit.type_history.items():
            if frame <= unit.finished_at:
                continue

            second = frame_to_second(frame)
            if second > limit_seconds:
                continue

            if "Flying" in unit_type.name:
                production_capacity_events.append((_get_unit_type(unit).name, second, -1))
                was_flying = True
            elif was_flying:
                production_capacity_events.append((_get_unit_type(unit).name, second, 1))
                was_flying = False
            elif "OrbitalCommand" in unit.name:
                production_capacity_events.append(
                    (_get_unit_type(unit).name, second - ORBITAL_TRANSFORMATION_DURATION, -1))
                production_capacity_events.append((_get_unit_type(unit).name, second, 1))
            elif "PlanetaryFortress" in unit.name:
                production_capacity_events.append(
                    (
                        _get_unit_type(unit).name,
                        second - PLANETARY_FORTRESS_TRANSFORMATION_DURATION,
                        -1))
                production_capacity_events.append((_get_unit_type(unit).name, second, 1))

    for unit in reactors:
        previous_structure_type = "Unknown"
        for frame, unit_type in unit.type_history.items():
            transformed_second = frame_to_second(frame)

            if transformed_second > limit_seconds:
                continue

            if previous_structure_type != "Unknown":
                production_capacity_events.append((previous_structure_type, transformed_second, -1))

            previous_structure_type = _get_structure_type(unit_type)

            if previous_structure_type != "Unknown":
                production_capacity_events.append((previous_structure_type, transformed_second, 1))

    production_capacity_events.sort(key=lambda x: x[1])

    return production_events, production_capacity_events


def production_used_out_of_capacity_for_player(
        limit_seconds: int,
        player: Player,
        replay: Replay) -> Dict[str, Tuple[List[Tuple[float, int]], List[Tuple[float, int]]]]:

    unit_events = [
        event
        for event
        in replay.events
        if (event.name in ["UnitBornEvent", "UnitDoneEvent"] and
            event.unit.owner == player)]

    produced_units = _extract_produced_units(unit_events)
    production_structures = _extract_production_structures(unit_events)

    if player.play_race == "Terran":
        reactors = set(
            event.unit
            for event
            in unit_events
            if "Reactor" in event.unit.name)

        production_used_events, production_capacity_events = _terran_production_used_and_capacity_events(
            replay,
            produced_units,
            production_structures,
            reactors,
            limit_seconds)
    else:
        production_used_events, production_capacity_events = [], []

    production_used = {}
    for structure_type, time, modified_production in production_used_events:
        if structure_type not in production_used:
            current_production = 0
            production_used[structure_type] = [(time - 0.00001, current_production)]
        else:
            current_production = production_used[structure_type][-1][1]

        production_used[structure_type].append((time, current_production + modified_production))

    production_capacity = {}
    for structure_type, time, modified_production_capacity in production_capacity_events:
        if structure_type not in production_capacity:
            current_production_capacity = 0
            production_capacity[structure_type] = [(time, current_production_capacity)]
        else:
            current_production_capacity = production_capacity[structure_type][-1][1]

        production_capacity[structure_type].append(
            (time, current_production_capacity + modified_production_capacity))

    analysis_end_second = min(limit_seconds, frame_to_second(replay.frames))

    for key in production_used.keys():
        production_used[key].append((analysis_end_second, production_used[key][-1][1]))

        if (key in production_capacity and
                production_capacity[key] and
                production_used[key] and
                    production_capacity[key][0][0] <= production_used[key][0][0]):
            production_used[key] = [(production_capacity[key][0][0], 0)] + production_used[key]

    for key in production_capacity.keys():
        production_capacity[key].append((analysis_end_second, production_capacity[key][-1][1]))

    return (
        OrderedDict(sorted(production_used.items(), key=_order_by_tech_tier)),
        OrderedDict(sorted(production_capacity.items(), key=_order_by_tech_tier)))


def production_used_till_time_for_player(
        limit_seconds: int, player: Player, replay: Replay) -> Dict[str, List[Tuple[float, int]]]:

    return production_used_out_of_capacity_for_player(limit_seconds, player, replay)[0]


def production_capacity_till_time_for_player(
        limit_seconds: int, player: Player, replay: Replay) -> Dict[str, List[Tuple[float, int]]]:

    return production_used_out_of_capacity_for_player(limit_seconds, player, replay)[1]
