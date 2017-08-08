import click
import sys
import ast
import pprint
import jenkins as jenkinsapi
from time import sleep
from tool_library.functions import startandmonitor


@click.command()
@click.option('--job',required=True, help='Name of the job to start and monitor.')
@click.option('--token',default=None, help='Token to access the job.')
@click.option('--wait',required=True, help='Time to wait between each request to check the build\'s status.',type=int)
@click.option('--parameters',required=False, help='Job\'s parameters.')
@click.pass_obj
def startAndMonitor(jenkins,job, parameters, wait, token):
    """Starts and monitors a Jenkins job until it is finished."""
    return startandmonitor(jenkins, job, parameters, wait, token)