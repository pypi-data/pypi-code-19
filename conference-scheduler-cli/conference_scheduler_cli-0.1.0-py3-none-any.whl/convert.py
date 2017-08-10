"""Utility functions to convert a solution to human readable form"""
from conference_scheduler import scheduler


def schedule_to_text(solution, events, slots):
    schedule = scheduler.solution_to_schedule(solution, events, slots)
    schedule.sort(key=lambda item: item.slot.starts_at)
    message = 'Schedule:\n\n'
    for item in schedule:
        message += (
            f'{item.event.name} at {item.slot.starts_at} in '
            f'{item.slot.venue}\n')
    return message
