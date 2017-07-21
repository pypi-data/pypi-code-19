import click
from tokens import send_request
from tabulate import tabulate

@click.group()
@click.pass_context
def service(ctx):
    pass


@service.command()
@click.argument('name')
@click.option('--version', default='latest')
@click.option('--label', '-l', multiple=True, help="<key>:<value>. Option can be used multiple times")
@click.pass_context
def create(ctx, name, version, label):
    """Create service NAME"""
    labels = {}
    for l in label:
        kv = l.split(':')
        labels[kv[0]] = kv[1]
    message = {'name': name, 'version': version, 'labels': labels}
    send_request(ctx, 'post', 'ns/{}/services'.format(ctx.obj['creds']['Namespace']), message)


@service.command()
@click.pass_context
def list(ctx):
    req = send_request(ctx, 'get', 'ns/{}/services'.format(ctx.obj['creds']['Namespace']))
    click.echo(tabulate(req.json(), headers='keys'))


@service.command()
@click.option('--id')
@click.pass_context
def delete(ctx, id):
    req = send_request(ctx, 'delete', 'ns/{}/services/{}'.format(ctx.obj['creds']['Namespace'], id))


def route_prefix(direct):
    if direct:
        return ''
    return 'activity/'


@service.group()
@click.option('--direct', is_flag=True, help="bypass nginx")
@click.pass_context
def activity(ctx, direct):
    ctx.obj['prefix'] = route_prefix(direct)


@activity.command()
@click.option('--id', default="")
@click.pass_context
def list(ctx, id):
    req = send_request(ctx, 'get', ctx.obj['prefix']+'ns/{}/services/'.format(ctx.obj['creds']['Namespace'])+id)
    if id:
        out = [req.json()]
    else:
        out = req.json()['items']
    for elem in out:
        elem['active_instances'] = len(elem['active_instances'])
    click.echo(tabulate(out, headers='keys'))


@activity.command()
@click.argument('id')
@click.pass_context
def instances(ctx, id):
    req = send_request(ctx, 'get',
                       ctx.obj['prefix']+'ns/{}/services/{}/instances'.format(ctx.obj['creds']['Namespace'], id))
    click.echo(tabulate(req.json()['items'], headers='keys'))


@activity.command()
@click.argument('id')
@click.pass_context
def inbound(ctx, id):
    req = send_request(ctx, 'get',
                       ctx.obj['prefix']+'ns/{}/services/{}/inbound'.format(ctx.obj['creds']['Namespace'], id))
    click.echo(tabulate(req.json()['items'], headers='keys'))


@activity.command()
@click.argument('id')
@click.pass_context
def outbound(ctx, id):
    req = send_request(ctx, 'get',
                       ctx.obj['prefix']+'ns/{}/services/{}/outbound'.format(ctx.obj['creds']['Namespace'], id))
    click.echo(tabulate(req.json()['items'], headers='keys'))
