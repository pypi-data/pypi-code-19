"""Procedures to define the Command Line Interface (cli)"""
from pathlib import Path

import click
from conference_scheduler.scheduler import event_schedule_difference
from conference_scheduler.converter import solution_to_schedule
from conference_scheduler.validator import (
    is_valid_solution, solution_violations)
import daiquiri

import scheduler.calculate as calc
from scheduler.decorators import timed
import scheduler.define as defn
from scheduler import convert, io, logging, session

logger = daiquiri.getLogger(__name__)


@click.version_option(message='%(prog)s %(version)s :: UK Python Association')
@click.group()
@click.option(
    '--verbosity', '-v', default='info',
    type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']),
    help='Logging verbosity')
def scheduler(verbosity):
    logging.setup(verbosity)


@scheduler.command()
@click.option(
    '--algorithm', '-a', default='pulp_cbc_cmd',
    type=click.Choice(
        ['pulp_cbc_cmd', 'glpk', 'hill_climber', 'simulated_annealing']),
    help='Solver algorithm')
@click.option(
    '--objective', '-o', default=None,
    type=click.Choice(['efficiency', 'equity', 'consistency']),
    help='Objective Function')
@click.option(
    '--input_dir', '-i', default=None, help='Directory for input files')
@click.option(
    '--solution_dir', '-s', default=None, help='Directory for solution files')
@click.option(
    '--build_dir', '-b', default=None, help='Directory for output yaml files')
@timed
def build(algorithm, objective, input_dir, solution_dir, build_dir):
    if input_dir:
        session.folders['input'] = Path(input_dir)

    if solution_dir:
        session.folders['solution'] = Path(solution_dir)

    if build_dir:
        session.folders['build'] = Path(build_dir)

    resources = defn.resources()
    slots = defn.slots(resources)
    events = defn.events(resources)
    unavailability = defn.unavailability(resources, slots)
    clashes = defn.clashes(resources)
    unsuitability = defn.unsuitability(resources, slots)
    allocations = defn.allocations(resources)

    defn.add_unavailability_to_events(events, slots, unavailability)
    defn.add_clashes_to_events(events, clashes)
    defn.add_unsuitability_to_events(events, slots, unsuitability)

    kwargs = {}
    if objective == 'consistency':
        original_solution = io.import_solution()
        defn.add_allocations(events, slots, original_solution, allocations)
        original_schedule = solution_to_schedule(
            original_solution, events, slots)
        kwargs['original_schedule'] = original_schedule

    solution = calc.solution(events, slots, algorithm, objective, **kwargs)

    if objective == 'consistency':
        schedule = solution_to_schedule(solution, events, slots)
        event_diff = event_schedule_difference(schedule, original_schedule)
        logger.debug(f'\nevent_diff:')
        for item in event_diff:
            logger.debug(f'{item.event.name} has moved from {item.old_slot.venue} at {item.old_slot.starts_at} to {item.new_slot.venue} at {item.new_slot.starts_at}')

    if solution is not None:
        defn.add_allocations(events, slots, solution, allocations)
        logger.debug(convert.schedule_to_text(solution, events, slots))
        io.export_solution_and_definition(resources, events, slots, solution)
        io.build_output(resources, events, slots, solution)


@scheduler.command()
@click.option(
    '--solution_dir', '-s', default=None, help='Directory for solution files')
@timed
def validate(solution_dir):
    if solution_dir:
        session.folders['solution'] = Path(solution_dir)

    solution = io.import_solution()
    definition = io.import_schedule_definition()
    logger.info('Validating schedule...')
    if is_valid_solution(solution, definition['events'], definition['slots']):
        logger.info('Imported solution is valid')
    else:
        for v in solution_violations(
                solution, definition['events'], definition['slots']):
            logger.error(v)


@scheduler.command()
@click.option(
    '--solution_dir', '-s', default=None, help='Directory for solution files')
@click.option(
    '--build_dir', '-b', default=None, help='Directory for output yaml files')
@timed
def rebuild(solution_dir, build_dir):
    if solution_dir:
        session.folders['solution'] = Path(solution_dir)

    if build_dir:
        session.folders['build'] = Path(build_dir)

    solution = io.import_solution()
    definition = io.import_schedule_definition()
    logger.info('Validating schedule...')
    if is_valid_solution(solution, definition['events'], definition['slots']):
        logger.info('Imported solution is valid')
        io.build_output(
            definition['resources'], definition['events'],
            definition['slots'], solution)
    else:
        for v in solution_violations(
                solution, definition['events'], definition['slots']):
            logger.error(v)
