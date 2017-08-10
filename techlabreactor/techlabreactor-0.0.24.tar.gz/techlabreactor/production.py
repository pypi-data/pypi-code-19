import itertools
import math
from collections import OrderedDict
from typing import Dict, Tuple, List

from sc2reader.data import Unit, UnitType
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

    if unit_name in ["Hellion", "Hellbat", "Cyclone", "SiegeTank", "Thor", "WidowMine"]:
        return "Factory"

    if unit_name in ["Medivac", "Viking", "Liberator", "Raven", "Banshee", "Battlecruiser"]:
        return "Starport"

    return "Unknown"


def _order_by_tech_tier(args):
    structure_type = args[0]
    return ["CommandCenter", "Barracks", "Factory", "Starport", "Unknown"].index(structure_type)


def production_used_till_time_for_player(
        second: int, player: Player, replay: Replay) -> Dict[str, List[Tuple[float, int]]]:

    if player.play_race in ["Protoss", "Zerg"]:
        return {}

    unit_events = [
        event
        for event
        in replay.events
        if (event.name in ["UnitBornEvent", "UnitDoneEvent"] and
            event.unit.owner == player)]

    produced_units_and_add_ons = set(
            event.unit
            for event
            in unit_events
            if (event.unit.finished_at > 0 and
                event.unit.name != "MULE" and
                ("TechLab" in event.unit.name or
                 "Reactor" in event.unit.name or
                 "Liberator" in event.unit.name or
                 "Cyclone" in event.unit.name or
                 event.unit.is_army or
                 event.unit.is_worker)))

    production_events = itertools.chain.from_iterable(
        [
            (_get_structure_type(_get_unit_type(unit)),
             frame_to_second(unit.finished_at) - _get_production_duration(_get_unit_type(unit), replay),
             1),
            (_get_structure_type(_get_unit_type(unit)),
             frame_to_second(unit.finished_at),
             -1)]
        for unit
        in produced_units_and_add_ons)

    event_stream = list(sorted(filter(lambda x: x[1] <= second, production_events), key=lambda x: x[1]))

    result = {}
    for structure_type, time, modified_production in event_stream:
        if structure_type not in result:
            current_production = 0
            result[structure_type] = [(time - 0.00001, current_production)]
        else:
            current_production = result[structure_type][-1][1]

        result[structure_type].append((time, current_production + modified_production))

    for key in result.keys():
        result[key].append((second, result[key][-1][1]))

    return OrderedDict(sorted(result.items(), key=_order_by_tech_tier))


def production_capacity_till_time_for_player(
        second: int, player: Player, replay: Replay) -> Dict[str, List[Tuple[float, int]]]:

    if player.play_race in ["Protoss", "Zerg"]:
        return {}

    unit_events = [
        event
        for event
        in replay.events
        if (event.name in ["UnitBornEvent", "UnitDoneEvent"] and
            event.unit.owner == player)]

    production_structures = set(
        event.unit
        for event
        in unit_events
        if _get_unit_type(event.unit).name in [
            "CommandCenter",
            "Barracks",
            "Factory",
            "Starport"
        ])

    reactors = set(
            event.unit
            for event
            in unit_events
            if "Reactor" in event.unit.name)

    production_capacity_events = []

    for unit in production_structures:
        production_capacity_events.append((_get_unit_type(unit).name, frame_to_second(unit.finished_at), 1))

        if unit.died_at is not None:
            production_capacity_events.append((_get_unit_type(unit).name, frame_to_second(unit.died_at), -1))

        was_flying = False
        for frame, unit_type in unit.type_history.items():
            if frame <= unit.finished_at:
                continue

            if "Flying" in unit_type.name:
                production_capacity_events.append((_get_unit_type(unit).name, frame_to_second(frame), -1))
                was_flying = True
            elif was_flying:
                production_capacity_events.append((_get_unit_type(unit).name, frame_to_second(frame), 1))
                was_flying = False
            elif "OrbitalCommand" in unit.name:
                production_capacity_events.append(
                    (_get_unit_type(unit).name, frame_to_second(frame) - ORBITAL_TRANSFORMATION_DURATION, -1))
                production_capacity_events.append((_get_unit_type(unit).name, frame_to_second(frame), 1))
            elif "PlanetaryFortress" in unit.name:
                production_capacity_events.append(
                    (_get_unit_type(unit).name, frame_to_second(frame) - PLANETARY_FORTRESS_TRANSFORMATION_DURATION, -1))
                production_capacity_events.append((_get_unit_type(unit).name, frame_to_second(frame), 1))

    for unit in reactors:
        previous_structure_type = "Unknown"
        for frame, unit_type in unit.type_history.items():
            if previous_structure_type != "Unknown":
                production_capacity_events.append((previous_structure_type, frame_to_second(frame), -1))

            previous_structure_type = _get_structure_type(unit_type)

            if previous_structure_type != "Unknown":
                production_capacity_events.append((previous_structure_type, frame_to_second(frame), 1))

    event_stream = sorted(filter(lambda x: x[1] <= second, production_capacity_events), key=lambda x: x[1])

    result = {}

    for structure_type, time, modified_production_capacity in event_stream:
        if structure_type not in result:
            current_production_capacity = 0
            result[structure_type] = [(time - 0.00001, current_production_capacity)]
        else:
            current_production_capacity = result[structure_type][-1][1]

        result[structure_type].append((time, current_production_capacity + modified_production_capacity))

    for key in result.keys():
        result[key].append((second, result[key][-1][1]))

    return OrderedDict(sorted(result.items(), key=_order_by_tech_tier))
