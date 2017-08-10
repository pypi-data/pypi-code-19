import daiquiri
from conference_scheduler import scheduler
from conference_scheduler.heuristics import hill_climber
from conference_scheduler.heuristics import simulated_annealing
from pulp import GLPK
from pulp import PULP_CBC_CMD

logger = daiquiri.getLogger(__name__)


def solution(events, slots, solver):
    logger.info(f'Scheduling conference using {solver} solver....')
    solvers = {
        'pulp_cbc_cmd': {
            'function': scheduler.solution,
            'kwargs': {
                'events': events,
                'slots': slots,
                'objective_function': None,
                'solver': PULP_CBC_CMD(msg=False)
            }
        },
        'glpk': {
            'function': scheduler.solution,
            'kwargs': {
                'events': events,
                'slots': slots,
                'objective_function': None,
                'solver': GLPK(msg=False)
            }
        },
        'hill_climber': {
            'function': scheduler.heuristic,
            'kwargs': {
                'events': events,
                'slots': slots,
                'objective_function': None,
                'algorithm': hill_climber
            }
        },
        'simulated_annealing': {
            'function': scheduler.heuristic,
            'kwargs': {
                'events': events,
                'slots': slots,
                'objective_function': None,
                'algorithm': simulated_annealing
            }
        },
    }
    try:
        solution = solvers[solver]['function'](**solvers[solver]['kwargs'])
    except ValueError:
        logger.error('No valid solution found')
        solution = None

    return solution
