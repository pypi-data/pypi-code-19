import sys

import click
import terminaltables

from bfcli.lib.api import API

@click.group()
def env():
  pass


@env.command()
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
