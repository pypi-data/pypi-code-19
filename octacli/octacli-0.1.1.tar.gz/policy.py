import click
from tokens import send_request
from tabulate import tabulate

@click.group()
@click.pass_context
def rule(ctx):
    pass


def split_type_val(s):
    type_val = s.split(':')
    val = type_val[1]
    if type_val[0] == 'labels':
        val = ':'.join(type_val[1:])
    print(type_val[0], val)
    return type_val[0], val

@rule.command()
@click.argument('source')
@click.argument('dest')
@click.pass_context
def create(ctx, source, dest):
    """Create SOURCE->DEST allowed Rule. Format: <'service'/'ip'/'url'/'labels'>:<value>
    service value is service id. ip value is ip or CIDR, url value is a domain name, labels are k:v,..."""
    source_type, source_val = split_type_val(source)
    dest_type, dest_val = split_type_val(dest)
    message = {'source': {'type': source_type, 'value': source_val},
               'destination': {'type': dest_type, 'value': dest_val}}
    send_request(ctx, 'post', 'ns/{}/policies'.format(ctx.obj['creds']['Namespace']), message)


@rule.command()
@click.pass_context
def list(ctx):
    req = send_request(ctx, 'get', 'ns/{}/policies'.format(ctx.obj['creds']['Namespace']))
    click.echo(tabulate(req.json(), headers='keys'))


@rule.command()
@click.option('--id')
@click.pass_context
def delete(ctx, id):
    req = send_request(ctx, 'delete', 'ns/{}/policies/{}'.format(ctx.obj['creds']['Namespace'], id))
