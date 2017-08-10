"""Functions which translate the human readable, nested definition data from
the input yaml files into the flattened structures required by the conference
scheduler computation engine."""

import itertools as it
from datetime import datetime
from datetime import timedelta

from conference_scheduler.resources import Event
from conference_scheduler.resources import Slot


def slot_times(event_types, session_times):
    return {
        event_type: [{
            'starts_at': slot_time['starts_at'],
            'duration': slot_time['duration'],
            'session_name': session_name}
            for session_name, slot_times in session_times[event_type].items()
            for slot_time in slot_times]
        for event_type in event_types}


def slots(event_types, venues, days, slot_times):
    return [
        Slot(
            venue=venue,
            starts_at=(
                datetime.combine(day, datetime.min.time())
                + timedelta(seconds=slot_time['starts_at'])
            ).strftime('%d-%b-%Y %H:%M'),
            duration=slot_time['duration'],
            session=f"{day} {slot_time['session_name']}",
            capacity=venues[venue]['capacity'])
        for event_type in event_types
        for venue, day, slot_time in it.product(
            venues, days, slot_times[event_type])
        if (event_type in venues[venue]['suitable_for'] and
            event_type in days[day]['event_types'])]


def events(events_definition):
    """
    Parameters
    ----------
    events_definition : list
        of dicts of the form
            {'title': Event title,
            'duration': <integer in minutes>,
            'tags': <list of strings>,
            'person': <string>}
    Returns
    -------
    list
        of Event instances
    """
    return [
        Event(
            event['title'], event['duration'], demand=None,
            tags=event['tags'])
        for event in events_definition]


def unavailability(events_definition, slots, unavailability_definition):
    """
    Parameters
    ----------
    events_definition : list
        of dicts of the form
            {'title': Event title,
            'duration': <integer in minutes>,
            'tags': <list of strings>,
            'person': <string>,
            'event_type': <string>}
    slots : list
        of Slot instances
    unavailablity_definition : dict
        mapping a person to a list of time periods. e.g.
            {'owen-campbell': [{
                'unavailable_from': datetime(2017, 10, 26, 0, 0),
                'unavailable_until': datetime(2017, 10, 26, 23, 59)}]
            }

    Returns
    -------
    dict
        mapping the index of an event in the events list to a list of slots
        for which it must not scheduled. The slots are represented by their
        index in the slots list.
    """
    return {
        events_definition.index(event): [
            slots.index(slot)
            for period in periods
            for slot in slots
            if period['unavailable_from'] <= datetime.strptime(slot.starts_at, '%d-%b-%Y %H:%M') and
            period['unavailable_until'] >= datetime.strptime(slot.starts_at, '%d-%b-%Y %H:%M') + timedelta(0, slot.duration * 60)
        ]
        for person, periods in unavailability_definition.items()
        for event in events_definition if event['person'] == person
    }


def clashes(events_definition, clashes_definition):
    """
     Parameters
    ----------
    events_definition : list
        of dicts of the form
            {'title': Event title,
            'duration': <integer in minutes>,
            'tags': <list of strings>,
            'person': <string>,
            'event_type': <string>}
    clashes_definition : dict
        mapping a person to a list of people whose events they must not not be
        scheduled against.

    Returns
    -------
    dict
        mapping the index of an event in the events list to a list of event
        indexes against which it must not be scheduled.
    """
    # Add everyone who is missing to the clashes definition so that they cannot
    # clash with themselves
    for person in [event['person'] for event in events_definition]:
        if person not in clashes_definition:
            clashes_definition[person] = [person]

    # Add the self-clashing constraint to any existing entries where it is
    # missing
    for person, clashing_people in clashes_definition.items():
        if person not in clashing_people:
            clashing_people.append(person)

    return {
        events_definition.index(event): [
            events_definition.index(t) for c in clashing_people
            for t in events_definition
            if t['person'] == c and
            events_definition.index(event) != events_definition.index(t)]
        for person, clashing_people in clashes_definition.items()
        for event in events_definition if event['person'] == person}


def unsuitability(venues, slots, events_definition):
    """
    Parameters
    ----------
    venues : dict
        mapping a venue name to a dict of further parameters
    events_definition : list
        of dicts of the form
            {'title': Event title,
            'duration': <integer in minutes>,
            'tags': <list of strings>,
            'person': <string>,
            'event_type': <string>}
    Returns
    -------
    dict
        mapping the index of an event in the events list to a list of slots
        for which it must not scheduled. The slots are represented by their
        index in the slots list.
    """
    unsuitability =  {
        events_definition.index(event): [
            slots.index(slot)
            for slot in slots
            if event['event_type'] not in venues[slot.venue]['suitable_for']
        ]
        for event in events_definition
    }
    return {
        event: unsuitable_slots
        for event, unsuitable_slots in unsuitability.items()
        if unsuitable_slots
    }
