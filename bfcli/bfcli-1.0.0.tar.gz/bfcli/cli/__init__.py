import click

from bfcli.cli import config, data, environment, job, node, project, resource, volume, workspace
import bfcli.config as c
from bfcli.lib.api import API
from bfcli.lib.cli_common import verbose_flag

@click.group()
def cli():
  pass


cli.add_command(config.version)
cli.add_command(verbose_flag(config.config))
cli.add_command(verbose_flag(config.login))
cli.add_command(verbose_flag(config.logout))
cli.add_command(environment.env)
cli.add_command(verbose_flag(workspace.workspace))
cli.add_command(verbose_flag(node.node))
cli.add_command(verbose_flag(resource.resource))
cli.add_command(verbose_flag(volume.volume))

if API.is_paas_enabled():
  cli.add_command(verbose_flag(data.data))
  cli.add_command(verbose_flag(job.info))
  cli.add_command(verbose_flag(job.rm))
  cli.add_command(verbose_flag(job.logs))
  cli.add_command(verbose_flag(job.run))
  cli.add_command(verbose_flag(job.status))
  cli.add_command(verbose_flag(job.stop))
  cli.add_command(verbose_flag(project.init))
  cli.add_command(verbose_flag(project.project))
