import logging

import click

from . import cli
from ..template import parse_yaml_files, create_resources_from_representations

logger = logging.getLogger(__name__)


@cli.command()
@click.option('-r', '--recursive', is_flag=True)
@click.option('-t', '--test', is_flag=True)
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def create(recursive, test, paths):
  logger.debug(f'Command: {__name__}:create recursive: {recursive} test: {test} paths: {paths}')
  representations = parse_yaml_files(paths, recursive, test)

  print('Documents in resolved order:')
  for representation in representations:
    print(representation)

  create_resources_from_representations(representations)


# @cli.command()
# @click.option('-r', '--recursive', is_flag=True)
# @click.option('-t', '--test', is_flag=True)
# @click.argument('files', type=click.Path(exists=True), nargs=-1)
# def delete(recursive, test, files):
#   print('Delete command')
#   print(recursive)
#   print(test)
#   print(files)
