import logging

import click

from . import cli
from ..jobs import run_calculation

logger = logging.getLogger(__name__)


@cli.command()
@click.argument('job')
@click.argument('uuid')
@click.option('--mode', type=click.Choice(['validate', 'initialize', 'run', 'full']), default='full')
@click.option('--temporary', 'temporary', flag_value=True, default=True)
@click.option('--permanent', 'temporary', flag_value=False)
def run(job, uuid, mode, temporary):
    logger.debug(f'Command {__name__}:run job: {job} uuid: {uuid} mode: {mode} temporary: {temporary}')
    # TODO use mode and temporary
    if job == 'calculation':
        run_calculation(uuid)
    else:
        raise ValueError('Unknown job type: ', job)
