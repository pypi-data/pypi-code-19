"""Functions and procedures to construct the definition of the conference
in a form suitable for the scheduling enging."""
from collections import Counter
from pprint import pformat

import daiquiri

import scheduler.denormalise as dn
from scheduler import io, session

logger = daiquiri.getLogger(__name__)


def resources():
    resources = io.import_yaml()
    resources['events'] = io.import_proposals(resources)
    return resources


def slots(resources):

    types_and_slots = dn.types_and_slots(resources['timetable'])
    logger.debug(f'\ntypes_and_slots:\n{pformat(types_and_slots)}')

    event_types = Counter([item['event_type'] for item in types_and_slots])
    for event_type, count in event_types.items():
        logger.info(f'{count} {event_type} slots available')
    return [item['slot'] for item in types_and_slots]


def events(resources):
    events = dn.types_and_events(resources['events'])
    logger.debug(f'\nevents:\n{pformat(events)}')

    event_types = Counter([item['event_type'] for item in events])
    for event_type, count in event_types.items():
        logger.info(f'{count} {event_type} events to schedule')
    return [item['event'] for item in events]


def unavailability(resources, slots):
    try:
        people_unavailability = dn.people_unavailability(
            resources['events'], slots, resources['unavailability']['people'])
    except KeyError:
        people_unavailability = {}
    logger.debug(f'\npeople_unavailability:\n{people_unavailability}')
    logger.info(f'{len(people_unavailability)} person(s) with unavailability')

    try:
        events_unavailability = dn.events_unavailability(
            resources['events'], slots, resources['unavailability']['events'])
    except KeyError:
        events_unavailability = {}
    logger.debug(f'\nevents_unavailability:\n{events_unavailability}')
    logger.info(f'{len(events_unavailability)} event(s) with unavailability')

    return {**people_unavailability, **events_unavailability}


def clashes(resources):
    try:
        people_clashes, count = dn.people_clashes(
            resources['events'], resources['clashes']['people'])
    except KeyError:
        people_clashes, count = {}, 0
    logger.debug(f'\npeople_clashes:\n{clashes}')
    logger.info(f'{count} person(s) with clashes')

    try:
        events_clashes = dn.events_clashes(
            resources['events'], resources['clashes']['events'])
    except KeyError:
        events_clashes = {}
    logger.debug(f'\nevents_clashes:\n{clashes}')
    logger.info(f'{count} event(s) with clashes')

    return {**people_clashes, **events_clashes}


def unsuitability(resources, slots):

    types_and_slots = dn.types_and_slots(resources['timetable'])

    unsuitability = dn.unsuitability(types_and_slots, resources['events'])
    logger.debug(f'\nunsuitability:\n{unsuitability}')
    logger.info(f'{len(unsuitability)} events with unsuitable timetable')
    return unsuitability


def allocations(resources):
    allocations = dn.allocations(resources['allocations'])
    logger.debug(f'\nallocations\n{allocations}')
    logger.info(f'{len(allocations)} pre-allocated event(s)')
    return allocations


def add_unavailability_to_events(events, slots, unavailability):
    for event, unavailable_slots in unavailability.items():
        events[event].add_unavailability(
            *[slots[s] for s in unavailable_slots])
    # logger.debug(f'\nevents with unavailability added:\n{pformat(events)}')
    logger.info(
        f'Added unavailability for {len(unavailability)} events.')


def add_clashes_to_events(events, clashes):
    for event, clashing_events in clashes.items():
        events[event].add_unavailability(*[events[t] for t in clashing_events])
    # logger.debug(f'\nevents with clashes added:\n{pformat(events)}')
    logger.info(f'Added clashes for {len(clashes)} event(s).')


def add_unsuitability_to_events(events, slots, unsuitability):
    for event, unsuitable_slots in unsuitability.items():
        events[event].add_unavailability(
            *[slots[s] for s in unsuitable_slots if unsuitable_slots])
    # logger.debug(f'\nevents with unsuitability added:\n{pformat(events)}')
    logger.info(
        f'Added unavailability for {len(unsuitability)} event(s) due to '
        'venue suitability.')


def add_allocations(events, slots, solution, allocations):
    for allocation in allocations:
        events.append(allocation['event'])

    for allocation in allocations:
        event_idx = events.index(allocation['event'])
        slot_idx = slots.index(allocation['slot'])
        solution.append((event_idx, slot_idx))

    logger.info(f'Added {len(allocations)} pre-allocated event(s) to solution')
