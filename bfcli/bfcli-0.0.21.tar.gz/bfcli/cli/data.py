import sys

import click
import terminaltables

from bfcli.lib.api import API, me
from bfcli.lib.cli_common import sort_flag

def print_data_object(data):
  pass


def print_data_list(data_list):
  headings = ['ID', 'Name', 'Created']
  table_data = [headings]

  for _d in data_list:
    table_data.append([_d.get('id'), _d.get('name'), _d.get('createdAt')])

  table = terminaltables.SingleTable(table_data, title='Data')
  click.echo(table.table)


@click.group()
def data():
  pass


@data.command()
@click.argument('path')
def upload(path):
  user = me()
  click.echo('Uploading data...')

  API.data.upload(path,
                  '/',
                  group_id=user.data['user']['defaultGroup'],
                  account_id=user.data['account']['id'])
  click.echo('Upload complete!')


@data.command()
@click.argument('id')
def rm(id):
  data = API.data.delete(id)
  click.echo('Deleted data {}'.format(id))


@data.command()
@sort_flag
def list(sort_created):
  data_list = API.data.list()
  if sort_created:
    data_list = sorted(data_list,
                       key=lambda d: d.get('createdAt'),
                       reverse=(sort_created == 'des'))

  table = terminaltables.SingleTable(API.data.get_table(data_list), title='Data')
  click.echo(table.table)
