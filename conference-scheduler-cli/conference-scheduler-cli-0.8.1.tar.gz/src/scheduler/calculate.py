import daiquiri
from conference_scheduler import scheduler
from conference_scheduler.heuristics import hill_climber
from conference_scheduler.heuristics import simulated_annealing
from conference_scheduler.lp_problem.objective_functions import (
    efficiency_capacity_demand_difference,
    equity_capacity_demand_difference,
    number_of_changes)
from pulp import GLPK
from pulp import PULP_CBC_CMD

logger = daiquiri.getLogger(__name__)

solvers = {
    'pulp_cbc_cmd': {
        'function': scheduler.solution,
        'kwargs': {
            'solver': PULP_CBC_CMD(msg=False)}},
    'glpk': {
        'function': scheduler.solution,
        'kwargs': {
            'solver': GLPK(msg=False)}},
    'hill_climber': {
        'function': scheduler.heuristic,
        'kwargs': {
            'algorithm': hill_climber}},
    'simulated_annealing': {
        'function': scheduler.heuristic,
        'kwargs': {
            'algorithm': simulated_annealing}}}

objectives = {
    'efficiency': efficiency_capacity_demand_difference,
    'equity': equity_capacity_demand_difference,
    'consistency': number_of_changes}


def solution(events, slots, solver, objective=None, **kwargs):
    message = f'Scheduling conference using {solver} solver'
    if objective is not None:
        message += f' and optimising {objective}'
    logger.info(f'{message}...')

    objective_function = objectives.get(objective, None)
    full_kwargs = {
        'events': events,
        'slots': slots,
        'objective_function': objective_function,
        **solvers[solver]['kwargs'],
        **kwargs}

    try:
        solution = solvers[solver]['function'](**full_kwargs)
    except ValueError:
        logger.error('No valid solution found')
        solution = None

    return solution
