import sys
import time

import click
import terminaltables

from bfcli.lib import user as user_lib
from bfcli.lib.api import API, auth_error_handler, me

@click.group()
def resource():
  pass


@resource.command()
@auth_error_handler
def info():
  # Build out the stats table
  user = me()
  resource_info = API.Resource.info(user.data['user']['defaultGroup'])
  stats_table_data = [
    ['Total', 'Max Local Only', 'Max Available'],
    []
  ]

  stats_table_data[1].append(resource_info['total_resources']/1000.0)
  stats_table_data[1].append(resource_info['max_local_resources']/1000.0)
  stats_table_data[1].append(resource_info['available_resources']/1000.0)

  # Build out the usage table
  nodes = API.Node.get_all()
  gpus = []
  for _n in nodes:
    gpus += _n.data.get('gpus', [])

  usage_table_data = [['GPU ID', 'Node ID', 'Workspace IDs', 'Usage %']]
  for _g in gpus:
    usage_table_data.append([_g['id'],
                             _g['node_id'],
                             [_r['workspace']['id'] for _r in _g['resources']],
                             str(_g['amount_allocated']/10) + '%'])


  usage_table = terminaltables.SingleTable(usage_table_data, title='Usage')
  stats_table = terminaltables.SingleTable(stats_table_data, title='Stats')

  if user_lib.show_resources():
    click.echo(usage_table.table)
    click.echo(stats_table.table)

  if 'user' in resource_info:
    user_resources = [
      ['Active GPUs', 'Remaining GPUs', 'Max GPUs'],
      []
    ]

    user_resources[1].append(resource_info['user']['active_resources']/1000.0)

    if resource_info['user']['max_resources'] != None:
      user_resources[1].append(resource_info['user']['remaining_resources']/1000.0)
      user_resources[1].append(resource_info['user']['max_resources']/1000.0)
    else:
      user_resources[1].append('Unlimited')
      user_resources[1].append('Unlimited')

    user_table = terminaltables.SingleTable(user_resources, title='User Limits')
    click.echo(user_table.table)
