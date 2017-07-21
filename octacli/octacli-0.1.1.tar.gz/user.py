import click
from tokens import send_request
from tabulate import tabulate

@click.group()
@click.pass_context
def user(ctx):
    pass


@user.command()
@click.argument('username')
@click.pass_context
def create(ctx, username):
    """"""
    message = {'name': username, 'role': 'admin'}
    send_request(ctx, 'post', 'ns/{}/users'.format(ctx.obj['creds']['Namespace']), message)

@user.command()
@click.pass_context
def list(ctx):
    req = send_request(ctx, 'get', 'ns/{}/users'.format(ctx.obj['creds']['Namespace']))
    click.echo(tabulate(req.json(), headers='keys'))


@user.command()
@click.option('--id')
@click.pass_context
def delete(ctx, id):
    req = send_request(ctx, 'delete', 'ns/{}/users/{}'.format(ctx.obj['creds']['Namespace'], id))
