import click
from tool_library.functions import queue


@click.command()
@click.pass_obj
def queue(jenkins):
    """Looks up Jenkin's queue."""
    queue(jenkins.url,jenkins.username,jenkins.password)
