import sys
import time

import click
import terminaltables

from bfcli import config
from bfcli.lib.api import API, enable_api_decorator

@click.group()
def resource():
  config.ensure_config_is_valid()
  enable_api_decorator()


@resource.command()
def info():
  # Build out the stats table
  resource_info = API.Resource.info()
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
    print(_g)
    usage_table_data.append([_g['id'],
                             _g['node_id'],
                             [_r['workspace']['id'] for _r in _g['resources']],
                             str(_g['amount_allocated']/10) + '%'])

  usage_table = terminaltables.SingleTable(usage_table_data, title='Usage')
  stats_table = terminaltables.SingleTable(stats_table_data, title='Stats')

  click.echo(usage_table.table)
  click.echo(stats_table.table)
