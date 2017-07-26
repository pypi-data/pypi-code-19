import sys

import click

from bfcli.lib.api import API, auth_error_handler

@click.group()
def volume():
  pass


@volume.command()
@auth_error_handler
def list():
  """Lists all volumes available"""
  volumes = API.Volume.get_all()

  output = ''

  for vol in volumes:
    output += str(vol)

  click.echo(output)


@volume.command()
@click.argument('id')
@auth_error_handler
def info(id):
  """Prints info on single volume"""
  vol = API.Volume.get(id)
  click.echo(str(vol))


@volume.command()
@click.option('--name', '-n', help='(Required) The name of this volume')
@click.option('--host-path', '-p', help='(Required) The path on the host')
@auth_error_handler
def add(name, host_path):
  """Make a new volume available"""
  vol = API.Volume.create(name=name, host_path=host_path)
  click.echo(str(vol))
