import csv
import pickle
from datetime import datetime
from pathlib import Path
from pprint import pformat

import daiquiri
from conference_scheduler import scheduler
from ruamel.yaml import YAML
from slugify import slugify

from scheduler.decorators import uses_output_folders
from scheduler import session

logger = daiquiri.getLogger(__name__)
yaml = YAML(typ='safe')
yaml.default_flow_style = False


def import_yaml():
    """Import all yaml files in the given folder into a single resources
    dict"""
    yaml_resources = {}
    yaml_files = [
        path for path in session.folders['input'].iterdir()
        if path.suffix == '.yml']
    for path in yaml_files:
        with path.open('r') as file:
            yaml_resources[path.stem] = yaml.load(file)
    logger.debug(f'\nreources:\n{pformat(yaml_resources)}')
    return yaml_resources


def import_proposals(resources):
    """Import the proposals data from a .csv file"""
    proposals = []
    with Path(session.folders['input'], 'proposals.csv').open('r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Session type'] in resources['event_types']:
                event_type = row['Session type']
                if event_type == 'workshop':
                    duration = 60
                else:
                    duration = 30
                proposals.append({
                    'title': row['Title'],
                    'duration': duration,
                    'person': slugify(row['Name']),
                    'tags': [],
                    'event_type': event_type
                })
    logger.debug(f'\nreources:\n{pformat(proposals)}')
    return proposals


@uses_output_folders
def pickle_solution_and_definition(resources, events, slots, solution):
    """Store the computed solution, the resources dict and the associated
    events and slots lists in pickle format"""
    pickle_file = Path(session.folders['solution'], 'scheduler.pickle')
    logger.info(
        f'Pickling resources, events, slots and schedule to {pickle_file}')
    bundle = {
        'resources': resources,
        'events': events,
        'slots': slots,
        'solution': solution
    }
    with pickle_file.open('wb') as f:
        pickle.dump(bundle, f, pickle.HIGHEST_PROTOCOL)


@uses_output_folders
def export_schedule(solution, events, slots):
    """Write a human readable .csv file of the computed solution"""
    csv_file = Path(session.folders['solution'], 'schedule.csv')
    logger.info(f'Exporting schedule to {csv_file}')

    schedule = scheduler.solution_to_schedule(solution, events, slots)
    scheduled_items = [
        {
            'event_index': events.index(item.event),
            'event': f'{item.event.name}',
            'slot_index': slots.index(item.slot),
            'slot': f'{item.slot.starts_at} {item.slot.venue}'
        }
        for item in schedule
    ]
    with csv_file.open('w') as f:
        writer = csv.DictWriter(
            f, fieldnames=['event_index', 'event', 'slot_index', 'slot'])
        writer.writeheader()
        for item in scheduled_items:
            writer.writerow(item)


@uses_output_folders
def build_output(resources, events, slots, solution):
    """Create the yaml files required by the conference django-amber based
    website for display of the programme"""
    logger.info(f'Creating output files in {session.folders["build"]}...')

    day_format = '%A %-d'
    slot_format = '%d-%b-%Y %H:%M'
    start_format = '%H:%M'

    for item in solution:
        slot_time = datetime.strptime(
            slots[item[1]].starts_at, slot_format)
        day = slot_time.strftime(day_format)
        start_time = slot_time.strftime(start_format)
        venue = slots[item[1]].venue

        content = {
            'chair': None,
            'room': venue,
            'date': day,
            'time': start_time,
            'title': events[item[0]].name
        }

        folder = Path(session.folders['build'], day, venue)
        folder.mkdir(parents=True, exist_ok=True)
        with Path(folder, start_time).open('a') as f:
            yaml.dump(content, f)
