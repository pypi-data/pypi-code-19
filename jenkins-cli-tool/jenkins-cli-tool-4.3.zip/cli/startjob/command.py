import click
import sys
import ast
import pprint
import jenkins as jenkinsapi
from time import sleep


@click.command()
@click.option('--job',required=True,help='Name of the job to start.')
@click.option('--parameters',required=False, help='Job\s parameters.')
@click.option('--token',default=None, help='Token to access the job.')
@click.pass_obj
def startjob(jenkins,job, parameters, token):
    """Starts a Jenkins job."""
    pp = pprint.PrettyPrinter(indent=4)
    server = jenkinsapi.Jenkins(jenkins.url, username=jenkins.username, password=jenkins.password)

    try:
        server.build_job(job, ast.literal_eval(parameters), token=token)
    except:
        pp.pprint(sys.exc_info())
        print "Please verify your parameters (especially choice parameters - are the values chosen authorized?"
        exit(2)
    print "%s build started." % (job)
