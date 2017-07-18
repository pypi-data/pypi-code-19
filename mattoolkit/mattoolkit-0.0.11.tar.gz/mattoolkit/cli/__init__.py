import click
import logging

from ..api import api as api_session
from ..logging import LOG_LEVELS, init_logging



@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--server', default=api_session.API_ROOT)
@click.option('--loglevel', type=click.Choice(LOG_LEVELS), default='WARNING')
@click.pass_context
def cli(ctx, debug, server, loglevel):
    ctx.obj['DEBUG'] = debug
    init_logging(loglevel)
    logger = logging.getLogger(__name__)
    logger.info(f'Setting API server with base url: {server}')
    if server.endswith('/'):
        server = server[:-1]
    api_session.API_ROOT = server


from .import auth
from . import template
from . import job
from . import api
