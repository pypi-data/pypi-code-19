import logging

import click

from . import cli
from ..template import (
  parse_yaml_files,
  create_resources_from_representations, delete_resources_from_representations,
  status_resources_from_representations, submit_resources_from_representations, cancel_resources_from_representations
)

logger = logging.getLogger(__name__)


@cli.command()
@click.option('-r', '--recursive', is_flag=True)
@click.option('-t', '--test', is_flag=True)
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def create(recursive, test, paths):
  logger.debug(f'Command: {__name__}:create recursive: {recursive} test: {test} paths: {paths}')
  representations = parse_yaml_files(paths, recursive)
  create_resources_from_representations(representations, test)


@cli.command()
@click.option('-r', '--recursive', is_flag=True)
@click.option('-t', '--test', is_flag=True)
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def delete(recursive, test, paths):
    logger.debug(f'Command: {__name__}:delete recursive: {recursive} paths: {paths}')
    representations = parse_yaml_files(paths, recursive)
    delete_resources_from_representations(representations, test)


# ================= Calculation Actions ====================


@cli.command()
@click.option('-r', '--recursive', is_flag=True)
@click.option('-c', '--check', is_flag=True)
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def status(recursive, check, paths):
  logger.debug(f'Command: {__name__}:status recursive: {recursive} paths: {paths} check: {check}')
  representations = parse_yaml_files(paths, recursive)
  status_resources_from_representations(representations, check)


@cli.command()
@click.option('-r', '--recursive', is_flag=True)
@click.option('-t', '--test', is_flag=True)
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def submit(recursive, test, paths):
  logger.debug(f'Command: {__name__}:submit recursive: {recursive} test: {test} paths: {paths}')
  representations = parse_yaml_files(paths, recursive)
  submit_resources_from_representations(representations, test)


@cli.command()
@click.option('-r', '--recursive', is_flag=True)
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def cancel(recursive, paths):
  logger.debug(f'Command: {__name__}:cancel recursive: {recursive} paths: {paths}')
  representations = parse_yaml_files(paths, recursive)
  cancel_resources_from_representations(representations)
