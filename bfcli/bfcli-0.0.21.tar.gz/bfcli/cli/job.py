import datetime
import os
import sys

import click
from dateutil import parser as dt_parser
import terminaltables

from bfcli.lib import local_project
from bfcli.lib.api import API, me
from bfcli.lib.cli_common import sort_flag
from bfcli.lib.environments import WS_TYPES

def print_single_job(job):
  table_data = [
    job.get_table_headers(),
    job.get_table_row()
  ]

  table = terminaltables.SingleTable(table_data, title='Run')
  click.echo(table.table)


def print_job_list(jobs):
  table_data = [API.Job.get_table_headers()]

  for _j in jobs:
    table_data.append(_j.get_table_row())

  table = terminaltables.SingleTable(table_data, title='Runs')
  click.echo(table.table)


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option('--project', '-p', help='The ID of the project to run under')
@click.option('--env', type=click.Choice(WS_TYPES), help='The container for running this command')
@click.option('--gpu', is_flag=True, help='Run this job with a GPU')
@click.option('--gpu-type', help='The type of GPU you want to use')
@click.option('--cpu', is_flag=True, help='Run this job CPU only')
@click.option('--data', '-d', help='CSV string of data IDs')
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def run(command, project, env, gpu, gpu_type, cpu, data):
  if gpu and cpu:
    click.echo('You cannot use the flags --cpu and --gpu together')
    sys.exit(1)
  elif not gpu and gpu_type:
    click.echo('You cannot specify gpu_type without the --gpu flag')
    sys.exit(1)

  if gpu:
    gpu_dev = {'type': 'gpu', 'value': 1}
    if gpu_type:
      gpu_dev['deviceType'] = gpu_type

    resources = [gpu_dev]
  else:
    resources = []


  if not project and not local_project.exists():
    click.echo('You need to be in a directory with a ".flex" file or ' + \
               'specify the project ID to run a job')
    sys.exit(1)

  if project:
    proj = API.Project.get(project)
    raise Exception('Cant do this yet')
  else:
    proj = local_project.get()
    click.echo('Uploading local project...')
    code_id = proj.upload_code(os.getcwd())
    click.echo('Uploading complete! Starting job...')

  user = me()
  data = ','.split(data) if data else []

  job = API.Job.create(
    proj.id,
    code_id,
    user.data['user']['defaultGroup'],
    env,
    data,
    resources,
    list(command),
  )

  print_single_job(job)


@click.command()
@click.argument('id')
@click.option('--tail', '-t', is_flag=True, help='Tail the job output')
def logs(id, tail):
  job = API.Job.get(id)
  click.echo(job.logs())


@click.command()
@click.argument('id')
def stop(id):
  job = API.Job.get(id)
  job.delete()
  job.reload()
  print_single_job(job)


@click.command()
@click.argument('id')
def info(id):
  job = API.Job.get(id)
  print_single_job(job)


@click.command()
@click.argument('id')
def rm(id):
  job = API.Job.get(id)
  job.delete()
  print_single_job(job)


@click.command()
@sort_flag
def status(sort_created):
  jobs = API.Job.get_all()
  if sort_created:
    jobs = sorted(jobs,
                  key=lambda j: j.data.get('createdAt'),
                  reverse=(sort_created == 'des'))

  print_job_list(jobs)
