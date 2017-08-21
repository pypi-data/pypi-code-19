"""Functions which translate the human readable, nested definition data from
the input yaml files into the flattened structures required by the conference
scheduler computation engine."""

from datetime import datetime
from datetime import timedelta

from conference_scheduler.resources import Event
from conference_scheduler.resources import Slot


def types_and_slots(timetable):
    """
    Parameters
    ----------
    timetable : dict
        of the form
            {
                <venue name>: {
                    <datetime of a day>: {
                        <session name>: {
                            'starts_at': <seconds after midnight>,
                            'duration': <minutes>,
                            'event_type': <event type>,
                            'capacity': <capacity
                        }
                    }
                }
            }
    Returns
    -------
    list
        of dicts mapping an event type to a Slot instance
    """
    return [
        {
            'event_type': slot['event_type'],
            'slot': Slot(
                venue=venue,
                starts_at=(
                    datetime.combine(day, datetime.min.time()) +
                    timedelta(seconds=slot['starts_at'])),
                duration=slot.get('duration', 0),
                session=f'{day} {session}',
                capacity=slot.get('capacity', 0))
        }
        for venue, days in timetable.items()
        for day, sessions in days.items()
        for session, slots in sessions.items()
        for slot in slots
    ]


def types_and_events(events_definition):
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
        of dicts mapping an event type to an Event instance
    """
    return [
        {
            'event_type': event['event_type'],
            'event': Event(
                name=event['title'],
                duration=event['duration'],
                demand=event['demand'],
                tags=event['tags'])
        }
        for event in events_definition]


def people_unavailability(events_definition, slots, unavailability_definition):
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
            if period['unavailable_from'] <= slot.starts_at and
            period['unavailable_until'] >= (
                slot.starts_at + timedelta(0, slot.duration * 60))
        ]
        for person, periods in unavailability_definition.items()
        for event in events_definition if event['person'] == person
    }


def events_unavailability(events_definition, slots, unavailability_definition):
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
        mapping an event to a list of time periods. e.g.
            {'An Interesting Talk': [{
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
            if period['unavailable_from'] <= slot.starts_at and
            period['unavailable_until'] >= (
                slot.starts_at + timedelta(0, slot.duration * 60))
        ]
        for event_title, periods in unavailability_definition.items()
        for event in events_definition if event['title'] == event_title
    }


def people_clashes(events_definition, clashes_definition):
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
    integer
        the count of self-clashes added
    """
    # Add everyone who is missing to the clashes definition so that they cannot
    # clash with themselves
    for person in [event['person'] for event in events_definition]:
        if person not in clashes_definition:
            clashes_definition[person] = [person]

    # Add the self-clashing constraint to any existing entries where it is
    # missing
    count = 0
    for person, clashing_people in clashes_definition.items():
        if person not in clashing_people:
            clashing_people.append(person)
            count += 1

    clashes = {
        events_definition.index(event): [
            events_definition.index(t) for c in clashing_people
            for t in events_definition
            if t['person'] == c and
            events_definition.index(event) != events_definition.index(t)]
        for person, clashing_people in clashes_definition.items()
        for event in events_definition if event['person'] == person
    }
    return clashes, count


def events_clashes(events_definition, clashes_definition):
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
        mapping an event to a list of events they must not not be
        scheduled against.

    Returns
    -------
    dict
        mapping the index of an event in the events list to a list of event
        indexes against which it must not be scheduled.
    """
    clashes = {
        events_definition.index(event): [
            events_definition.index(t) for c in clashing_events
            for t in events_definition
            if t['title'] == c and
            events_definition.index(event) != events_definition.index(t)]
        for event_title, clashing_events in clashes_definition.items()
        for event in events_definition if event['title'] == event_title
    }
    return clashes


def unsuitability(types_and_slots, events_definition):
    """
    Parameters
    ----------
    types_and_slots : list
        of dicts mapping an event type to a Slot instance
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
    output = {}
    for i, event in enumerate(events_definition):
        unsuitable_slots = [
            i for i, dictionary in enumerate(types_and_slots)
            if dictionary['event_type'] != event['event_type']]
        output[i] = unsuitable_slots
    return output


def allocations(allocations_definition):
    try:
        return [
            {
                'event': Event(
                    name=event,
                    duration=0,
                    demand=0,
                    tags=details['tags']),
                'slot': Slot(
                    venue=details['venue'],
                    starts_at=(datetime.combine(
                        details['day'],
                        datetime.min.time()) +
                        timedelta(seconds=details['starts_at'])),
                    duration=0,
                    session=(f'{details["day"]} {details["session"]}'),
                    capacity=0)
            }
            for allocation in allocations_definition
            for event, details in allocation.items()]
    except TypeError:
        return []
