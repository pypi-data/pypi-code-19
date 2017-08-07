import logging

import click

from . import cli
from ..jobs import run_calculation

logger = logging.getLogger(__name__)

def validate_cores(ctx, param, value):
    cores = int(value)
    if cores < 0:
        raise click.BadParameter('cores must be positive')
    return cores


@cli.command()
@click.argument('job')
@click.argument('uuid')
@click.option('--mode', type=click.Choice(['validate', 'initialize', 'run', 'full']), default='full')
@click.option('--temporary/--permanent', 'temporary', default=True)
@click.option('--cores', type=int, default=-1)
def run(job, uuid, mode, temporary, cores):
    """ Negative cores indicates default

    """
    logger.info(f'Command {__name__}:run job: {job} uuid: {uuid} mode: {mode} temporary: {temporary} cores: {cores}')

    # TODO use mode and temporary
    if job == 'calculation':
        run_calculation(uuid, mode=mode, temporary=temporary, cores=cores)
    else:
        raise ValueError('Unknown job type: ', job)
