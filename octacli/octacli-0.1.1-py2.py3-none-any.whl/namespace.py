import click
import base64
from tokens import send_request
from tabulate import tabulate


@click.group()
@click.pass_context
def namespace(ctx):
    pass


@namespace.command()
@click.argument('name')
@click.argument('username')
@click.pass_context
def create(ctx, name, username):
    """Create namespace NAME and account manager USERNAME"""
    message = {'ns': {'name': name}, 'manager': {'name': username, 'role': 'manager'}}
    req = send_request(ctx, 'post', 'namespaces', message)
    click.echo(req.json())

@namespace.command()
@click.pass_context
def list(ctx):
    req = send_request(ctx, 'get', 'namespaces')
    click.echo(tabulate(req.json(), headers='keys'))


@namespace.command()
@click.option('--id')
@click.pass_context
def delete(ctx, id):
    req = send_request(ctx, 'delete', 'namespaces/{}'.format(id))
