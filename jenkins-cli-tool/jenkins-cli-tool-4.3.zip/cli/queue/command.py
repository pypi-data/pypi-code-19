import click
import sys
import ast
import pprint
import jenkins as jenkinsapi
from time import sleep


@click.command()
@click.pass_obj
def queue(jenkins):
    """Looks up Jenkin's queue."""
    pp = pprint.PrettyPrinter(indent=4)
    server = jenkinsapi.Jenkins(jenkins.url, username=jenkins.username, password=jenkins.password)
    queue_info = server.get_queue_info()
    pp = pprint.PrettyPrinter(indent=4)
    click.echo("Queue trace:")
    pp.pprint(queue_info)