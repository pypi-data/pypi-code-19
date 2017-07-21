import click
from tokens import send_request
from tabulate import tabulate


def route_prefix(direct):
    if direct:
        return ''
    return 'activity/'


@click.group()
@click.option('--direct', is_flag=True, help="bypass nginx")
@click.pass_context
def alert(ctx, direct):
    ctx.obj['prefix'] = route_prefix(direct)


@alert.command()
@click.option('--service-id')
@click.pass_context
def list(ctx, service_id):
    service_selector = ""
    if service_id:
        service_selector = 'services/' + 'service_id/'
    req = send_request(ctx, 'get',
                       ctx.obj['prefix']+'ns/{}/{}alerts'.format(ctx.obj['creds']['Namespace'], service_selector))
    click.echo(tabulate(req.json()['items'], headers='keys'))
