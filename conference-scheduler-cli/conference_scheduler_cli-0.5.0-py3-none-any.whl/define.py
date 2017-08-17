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

    types_and_slots = dn.types_and_slots(resources['venues'])
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
    unavailability = dn.unavailability(
        resources['events'], slots, resources['unavailability'])
    logger.debug(f'\nunavailability:\n{unavailability}')
    logger.info(f'{len(unavailability)} person(s) with unavailability')
    return unavailability


def clashes(resources):
    clashes, count = dn.clashes(resources['events'], resources['clashes'])
    logger.debug(f'\nclashes:\n{clashes}')
    logger.info(f'{count} person(s) with clashes')
    return clashes


def unsuitability(resources, slots):

    types_and_slots = dn.types_and_slots(resources['venues'])

    unsuitability = dn.unsuitability(types_and_slots, resources['events'])
    logger.debug(f'\nunsuitability:\n{unsuitability}')
    logger.info(f'{len(unsuitability)} events with unsuitable venues')
    return unsuitability


def add_unavailability_to_events(events, slots, unavailability):
    for event, unavailable_slots in unavailability.items():
        events[event].add_unavailability(
            *[slots[s] for s in unavailable_slots])
    # logger.debug(f'\nevents with unavailability added:\n{pformat(events)}')
    logger.info(
        f'Added unavailability for {len(unavailability)} person(s) to events.')


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
