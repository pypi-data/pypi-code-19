import click
import colorama

from mit.commands.branch import Branch
from mit.commands.checkout import Checkout
from mit.commands.fetch import Fetch
from mit.commands.pull import Pull
from mit.commands.rebase import Rebase
from mit.commands.stash import Stash
from mit.commands.status import Status


@click.group()
@click.version_option()
def cli():
    """Mit.

    Python tool for batch execution of git commands
    """
    colorama.init()


@cli.command()
def status():
    Status().run()


@cli.command()
def pull():
    Pull().run()


@cli.command()
@click.argument('branch_name')
def checkout(branch_name):
    Checkout(branch_name).run()


@cli.command()
def fetch():
    Fetch().run()


@cli.command()
def branch():
    Branch().run()


@cli.command()
@click.argument('from_branch')
@click.argument('to_branch')
def rebase(from_branch, to_branch):
    Rebase(from_branch, to_branch).run()


@cli.command()
def update():
    Fetch().run(False)
    Stash(Stash.Type.STASH).run()
    Pull().run(False)
    Stash(Stash.Type.POP).run()
    Status().run()
