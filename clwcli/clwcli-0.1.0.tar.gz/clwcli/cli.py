import click
from subprocess import call
from clwcli.utils import get_public_dns_name


@click.group()
def cli():
    pass


@cli.group('emp', help='Empire extensions')
def empire():
    pass


@empire.command('deploy', help='An extensions of `emp deploy`')
@click.argument('app_name')
def deploy(app_name):
    call(['emp', 'create', app_name])
    call(['emp', 'domain-add', app_name + '.clw', '-a', app_name])
    call(['emp', 'deploy', 'tuyenhx/' + app_name])


@empire.command('apps', help='Call `emp apps`')
def apps():
    cmd = ['emp', 'apps']
    call(cmd)


@empire.command('get-dns', help='Get public dns of deployed application')
@click.argument('app_name', required=False)
def get_dns(app_name):
    results = get_public_dns_name(app_name)
    click.echo(results)


def main():
    cli()
