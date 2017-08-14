"""Functions and procedures to construct the definition of the conference
in a form suitable for the scheduling enging."""
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
    slot_times = dn.slot_times(
        resources['event_types'], resources['session_times'])
    logger.debug(f'\nslot times:\n{pformat(slot_times)}')

    slots = dn.slots(
        resources['event_types'], resources['venues'], resources['days'],
        slot_times)
    logger.debug(f'\nslots:\n{pformat(slots)}')
    logger.info(f'{len(slots)} slots available')
    return slots


def events(resources):
    events = dn.events(resources['events'])
    logger.debug(f'\nevents:\n{pformat(events)}')
    logger.info(f'{len(events)} events to schedule')
    return events


def unavailability(resources, slots):
    unavailability = dn.unavailability(
        resources['events'], slots, resources['unavailability'])
    logger.debug(f'\nunavailability:\n{unavailability}')
    logger.info(f'{len(unavailability)} person(s) with unavailability')
    return unavailability


def clashes(resources):
    clashes = dn.clashes(resources['events'], resources['clashes'])
    logger.debug(f'\nclashes:\n{clashes}')
    logger.info(f'{len(clashes)} person(s) with clashes')
    return clashes


def unsuitability(resources, slots):
    unsuitability = dn.unsuitability(
        resources['venues'], slots, resources['events'])
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
