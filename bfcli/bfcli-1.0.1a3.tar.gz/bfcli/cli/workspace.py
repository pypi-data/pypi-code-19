import datetime
import sys

import click
import terminaltables

from bfcli import config
from bfcli.lib import analytics
from bfcli.lib.api import API, me, auth_error_handler
from bfcli.lib.cli_common import sort_flag
from bfcli.lib.environments import WS_TYPES

@click.group()
def workspace():
  pass


@workspace.command()
@click.argument('id')
@config.validate_config
@auth_error_handler
def rm(id):
  """Deletes the workspace with the given ID."""
  ws = API.Workspace.get(id)
  now = datetime.datetime.utcnow()

  try:
    ws.delete()
  except Exception as e:
    analytics.track('WORKSPACE_REMOVE_FAIL', {
      'ui': 'cli',
      'createdAt': ws.data['start_date'],
      'deletedAt': now,
      'environment': ws.data['type'],
    })

    raise e

  analytics.track('WORKSPACE_REMOVE_SUCCESS', {
    'ui': 'cli',
    'createdAt': ws.data['start_date'],
    'deletedAt': now,
    'environment': ws.data['type'],
  })

  click.echo('Deleted workspace:' + str(ws))


@workspace.command()
@click.argument('id')
@click.option('--name', '-n', help='(Required) The name of the new environment.')
@config.validate_config
@auth_error_handler
def save(id, name):
  """Saves the workspace as a new environment available to run."""
  if not name:
    click.echo('You must provide the name argument in order to save the workspace')
    sys.exit(1)

  ws = API.Workspace.get(id)
  ws.save(name)
  click.echo('Saved workspace:' + str(ws))


@workspace.command()
@click.argument('id')
@config.validate_config
@auth_error_handler
def info(id):
  """Prints the workspace with the given ID"""
  ws = API.Workspace.get(id)
  click.echo(str(ws))


@workspace.command()
@sort_flag
@config.validate_config
@auth_error_handler
def list(sort_created):
  """List all of the currently running workspaces"""
  spaces = API.Workspace.get_all()
  if sort_created:
    spaces = sorted(spaces,
                    key=lambda ws: ws.data.get('start_date'),
                    reverse=(sort_created == 'des'))

  output = ''

  if not spaces:
    click.echo('\nNo active workspaces\n')
    return

  for ws in spaces:
    output += str(ws)

  click.echo(output)


@click.argument('platform_type', type=click.Choice(WS_TYPES))
@click.option('--name', '-N', help='The name for your workspace. If not given, it will be auto generated')
@click.option('--gpus', '-g', type=float, help='The number of GPUs to use with your workspace. You can enter: 0, 0.5, 1, 2, 3, ...')
@config.validate_config
@auth_error_handler
def create(platform_type, name, gpus, **kwargs):
  """Runs a workspace on a node"""
  user = me()
  now = datetime.datetime.utcnow()

  if gpus:
    if (gpus < 1 and not (gpus == 0 or gpus == 0.5)) or \
       (gpus > 1 and gpus % 1 > 0):
      click.echo('You can only enter 0, 0.5, or a positive integer for the number of GPUs')
      sys.exit(1)

    gpus = int(gpus * 1000)

  meta = API.Workspace.image_metadata(platform_type)
  is_custom_env = True if 'id' in meta else False
  options = {}
  for param in meta.get('parameters', []):
    if 'user_input' in param:
      field_prompt = param.get('display', param['key'])
      val = click.prompt('Enter {}'.format(field_prompt))
      options[param['key']] = val

  try:
    ws = API.Workspace.create(platform_type,
                              user.data['user']['defaultGroup'],
                              name=name,
                              gpus=gpus,
                              options=options)
  except Exception as e:
    analytics.track('WORKSPACE_CREATE_FAIL', {
      'ui': 'cli',
      'createdAt': now,
      'customEnvironment': is_custom_env,
      'environment': platform_type,
      'gpus': gpus / 1000.0 if gpus else 0,
    })

    raise e

  local_node_id = ws.data['node_id']
  local_gpus = 0
  remote_gpus = 0
  for resource in ws.data.get('resources', []):
    if resource.get('gpu', {}).get('node_id') == local_node_id:
      local_gpus += resource['allocation_amount']
    else:
      remote_gpus += resource['allocation_amount']

  analytics.track('WORKSPACE_CREATE_SUCCESS', {
    'ui': 'cli',
    'createdAt': now,
    'customEnvironment': is_custom_env,
    'environment': platform_type,
    'gpus': gpus / 1000.0 if gpus else 0,
    'localGpus': local_gpus / 1000.0,
    'remoteGpus': remote_gpus / 1000.0
  })

  click.echo(str(ws))


try:
  node_select = API.public_config()['simple_mode_node_type_selection'].lower() == 'true'
except:
  node_select = False

if node_select:
  click.option('--run-on-cpu',
               '-c',
               is_flag=True,
               help='Force workspace to run on a CPU node.')(create)
  click.option('--node',
               '-n',
               'node_id',
               type=int,
               help='The ID of the Node to run this workspace on. Takes precedent over --run-on-cpu flag')(create)

workspace.command()(create)
