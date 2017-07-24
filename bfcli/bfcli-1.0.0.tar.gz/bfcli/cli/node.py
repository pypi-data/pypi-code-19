import sys
import time

import click

from bfcli import config
from bfcli.lib.api import API, enable_api_decorator

@click.group()
def node():
  config.ensure_config_is_valid()
  enable_api_decorator()


@node.command()
def list():
  """Lists all nodes in cluster"""
  nodes = API.Node.get_all()

  output = ''

  for n in nodes:
    output += str(n)

  click.echo(output)


@node.command()
@click.argument('id')
def info(id):
  """Prints info on single node"""
  node = API.Node.get(id)
  click.echo(str(node))


#@node.command()
#@click.argument('ip')
#def add(ip):
#  """Add's the node to the cluster"""
#  API.Node.add_by_ip(ip)
#
#  click.echo('Successfully added node. Waiting 3 seconds for data to populate...')
#  time.sleep(3)
#
#  nodes = API.Node.get_all()
#  for n in nodes:
#    if n.data['ip_address'] == ip:
#      click.echo(str(n))
#      sys.exit()
#
#  click.echo('Node data has not yet populated. Try running `zamboni node list` later to get info.')
#  sys.exit(1)


def remove(id):
  """Removes a single node"""
  node = API.Node.get(id)
  node.delete()

  click.echo('Removed Node {}'.format(node.id))
