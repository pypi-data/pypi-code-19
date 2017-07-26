import sys

import click
import terminaltables

from bfcli import config
from bfcli.lib.api import API, auth_error_handler

@click.group()
def env():
  pass


@env.command()
@config.validate_config
@auth_error_handler
def list():
  images = API.Workspace.images()

  headers = ['Name', 'Program Version', 'CUDA Version', 'CUDNN Version', 'OS']
  table_data = [headers]

  for img in images:
    table_data.append([img.get('type', ''),
                       img.get('version', ''),
                       img.get('cuda_version', ''),
                       img.get('cudnn_version', ''),
                       img.get('operating_system', '')])

  table = terminaltables.SingleTable(table_data, title='Environments')
  click.echo(table.table)
