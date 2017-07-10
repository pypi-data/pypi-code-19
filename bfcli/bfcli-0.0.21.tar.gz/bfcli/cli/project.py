import json
import os
import sys

import click
import terminaltables

from bfcli.lib import local_project
from bfcli.lib.api import API
from bfcli.lib.cli_common import sort_flag

def single_project_print(project):
  table_data = [API.Project.get_table_headers(), project.get_table_row()]
  table = terminaltables.SingleTable(table_data, title='Project')
  click.echo(table.table)


def many_projects_print(projects):
  table_data = [API.Project.get_table_headers()]

  for _p in projects:
    table_data.append(_p.get_table_row())

  table = terminaltables.SingleTable(table_data, title='Projects')
  click.echo(table.table)


@click.command()
@click.argument('name')
def init(name):
  if local_project.exists():
    error = 'There is a {} file in this directory.\n' + \
            'Delete the file and rerun init if you want to make a new project'
    click.echo(error.format(local_project.PROJECT_FILE))
    sys.exit(1)

  project = None
  p_file = local_project.path()

  try:
    with open(p_file, 'w') as _f:
      project = API.Project.create(name)
      _f.write(json.dumps(project.data, indent=2))
  except Exception as e:
    os.remove(p_file)
    click.echo('Failed to create the project')
    sys.exit(1)

  click.echo('Project {} initialized in the current directory'.format(name))


@click.group()
def project():
  pass


@project.command()
@click.option('--id', help='The project ID')
@click.option('--force', '-f', is_flag=True, help='Force remove the .flex file in this directory')
def rm(id, force):
  if not id and not local_project.exists():
    click.echo('You need to be in a directory with a ".flex" file or ' + \
               'specify the project ID to delete the project')
    sys.exit(1)

  proj = None

  if id:
    proj = API.Project.get(id)
  else:
    try:
      proj = local_project.get()
    finally:
      if proj or force:
        local_project.remove()

  proj.delete()
  single_project_print(proj)


@project.command()
@sort_flag
def list(sort_created):
  projects = API.Project.get_all()
  if sort_created:
    projects = sorted(projects,
                      key=lambda p: p.data.get('createdAt'),
                      reverse=(sort_created == 'des'))

  many_projects_print(projects)


@project.command()
@click.option('--id', help='The project ID')
def info(id):
  if not id and not local_project.exists():
    click.echo('You need to be in a directory with a ".flex" file or ' + \
               'specify the project ID to get project info')
    sys.exit(1)

  if id:
    proj = API.Project.get(id)
  else:
    proj = local_project.get()

  single_project_print(proj)
