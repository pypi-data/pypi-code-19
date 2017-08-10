"""Procedures to define the Command Line Interface (cli)"""
import time
from pathlib import Path

import click
import daiquiri

import scheduler.calculate as calc
import scheduler.define as defn
from scheduler import convert, io, logging, session

logger = daiquiri.getLogger(__name__)


@click.version_option(message='%(prog)s %(version)s :: UK Python Association')
@click.group()
@click.option(
    '--verbosity', '-v', default='info',
    type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']),
    help='Logging verbosity')
@click.option(
    '--solution_dir', '-s', default=None, help='Directory for solution files')
def scheduler(verbosity, solution_dir):
    if solution_dir:
        session.folders['solution'] = Path(solution_dir)
    logging.setup(verbosity)


@scheduler.command()
@click.option(
    '--solver', '-s', default='pulp_cbc_cmd',
    type=click.Choice(
        ['pulp_cbc_cmd', 'glpk', 'hill_climber', 'simulated_annealing']),
    help='Solver algorithm')
@click.option(
    '--input_dir', '-i', default=None, help='Directory for input files')
@click.option(
    '--build_dir', '-b', default=None, help='Directory for output yaml files')
def build(solver, input_dir, build_dir):
    start_time = time.time()

    if input_dir:
        session.folders['input'] = Path(input_dir)

    if build_dir:
        session.folders['build'] = Path(build_dir)

    resources = defn.resources()
    slots = defn.slots(resources)
    events = defn.events(resources)
    unavailability = defn.unavailability(resources, slots)
    clashes = defn.clashes(resources)
    unsuitability = defn.unsuitability(resources, slots)

    defn.add_unavailability_to_events(events, slots, unavailability)
    defn.add_clashes_to_events(events, clashes)
    defn.add_unsuitability_to_events(events, slots, unsuitability)

    solution = calc.solution(events, slots, solver)

    if solution is not None:
        logger.debug(convert.schedule_to_text(solution, events, slots))
        io.pickle_solution_and_definition(resources, events, slots, solution)
        io.export_schedule(solution, events, slots)
        io.build_output(resources, events, slots, solution)

    elapsed_time = time.time() - start_time
    logger.info(f'Completed in {round(elapsed_time, 2)}s')
