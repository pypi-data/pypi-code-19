import click

from glob import glob
from os import path
from yaml import dump

from config import Config
from stack import Stack
from template import Template
from assets import send_assets

# Brume Configuration
conf = {}
templates_config = {}
cf_config = {}
current_path = None

def process_assets():
    """Send assets if defined."""
    global conf
    global current_path
    if ('assets' in conf):
        assetsConfig = conf['assets']
        local_path = assetsConfig['local_path']
        s3_bucket = assetsConfig['s3_bucket']
        s3_path = assetsConfig['s3_path']
        click.echo("Processing assets from {} to s3://{}/{}".format(path.join(current_path, local_path), s3_bucket, s3_path))
        send_assets(local_path, s3_bucket , s3_path)

def collect_templates():
    """Convert every .cform template into a Template."""
    global templates_config
    global current_path
    templates = glob(path.join(current_path, templates_config.get('local_path', ''), '*.cform'))
    return [Template(t, templates_config, current_path) for t in templates]


def validate_and_upload():
    """Validate templates and upload new stack configuration."""
    templates = collect_templates()
    map(lambda t: t.validate(), templates)
    map(lambda t: t.upload(), templates)
    process_assets()

def newStack():
    """Instanciante main Stack."""
    global cf_config
    global current_path
    return Stack(cf_config, current_path)

@click.command()
def config():
    """Print the current stack confguration."""
    global conf
    print(dump(conf))


@click.command()
def create():
    """Create a new CloudFormation stack."""
    validate_and_upload()
    newStack().create()


@click.command()
def update():
    """Update an existing CloudFormation stack."""
    validate_and_upload()
    newStack().update()


@click.command()
def deploy():
    """Create or update a CloudFormation stack."""
    validate_and_upload()
    newStack().create_or_update()


@click.command()
def delete():
    """Delete a CloudFormation stack."""
    newStack().delete()


@click.command()
def status():
    """Get the status of a CloudFormation stack."""
    newStack().status()


@click.command()
def outputs():
    """Get the full list of outputs of a CloudFormation stack."""
    outputs = newStack().outputs()
    print dump(outputs, default_flow_style=False)


@click.command()
def parameters():
    """Get the full list of parameters of a CloudFormation stack."""
    global cf_config
    parameters = newStack().params()
    print dump(parameters, default_flow_style=False)


@click.command()
def validate():
    """Validate CloudFormation templates."""
    templates = collect_templates()
    return map(lambda t: t.validate(), templates)


@click.command()
def upload():
    """Upload CloudFormation templates and assets to S3."""
    process_assets()
    templates = collect_templates()
    return map(lambda t: t.upload(), templates)


@click.group()
@click.option('--configuration', default='brume.yml')
def cli(configuration):
    global conf
    global templates_config
    global cf_config
    global current_path
    conf = Config.load(configuration)
    templates_config = conf['templates']
    cf_config = conf['stack']
    current_path = path.dirname(configuration)
    pass


cli.add_command(create)
cli.add_command(update)
cli.add_command(deploy)
cli.add_command(upload)
cli.add_command(delete)
cli.add_command(validate)
cli.add_command(config)
cli.add_command(status)
cli.add_command(outputs)
cli.add_command(parameters)

if __name__ == '__main__':
    cli()
