import click
from tool_library.functions import startjob



@click.command()
@click.option('--job',required=True,help='Name of the job to start.')
@click.option('--parameters',required=False, help='Job\s parameters.')
@click.option('--token',default=None, help='Token to access the job.')
@click.pass_obj
def startjob(jenkins,job, parameters, token):
    """Starts a Jenkins job."""
    startjob(jenkins.url, jenkins.username, jenkins.password)

