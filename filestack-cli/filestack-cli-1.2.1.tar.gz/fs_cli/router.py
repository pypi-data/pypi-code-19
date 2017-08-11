try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import click
import json
import os
import pprint
import sys

from fs_cli.config import CONFIG_PATH
from fs_cli.utils import management_utils
from filestack import Client, security

def set_config(parser, environment, key, value):
    try:
        parser[environment].update({
            key: value
        })
    except AttributeError:
        if sys.version_info[0] < 3 and environment.lower() == 'default':
            environment = configparser.DEFAULTSECT

        parser.set(environment, key, value)

# this helps pass the context to children commands
# and helps us control how we name/call commands
# in the future
class Alias(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)

        if rv is not None:
            return rv


# base command "fs-cli" defines and then passes all global
# options to children commands
@click.command(cls=Alias)
@click.option('-e', '-environment', default='default')
def cli(environment):
    pass


"""
    COMMANDS:
    [fs-cli] calls children commands and processes global options (like environment)
        [manage] -- handles all app and account functions
            [create_app] -- creates an app
            [list_apps] -- lists all apps based on given environment
        [upload] -- uploads local files
"""

@cli.command()
@click.pass_context
def init(ctx):

    environment = ctx.parent.params['environment'] or 'default'
    config_parser = configparser.ConfigParser()


    apikey = click.prompt('Please enter the apikey for your environment', type=str)

    try:
        config_parser[environment] = {'apikey': apikey}
    except AttributeError:
        if sys.version_info[0] < 3 and environment.lower() == 'default':
            config_parser.set(configparser.DEFAULTSECT, 'apikey', apikey)
        else:
            config_parser.add_section(environment)
            config_parser.set(environment, 'apikey', apikey)

    if click.confirm('Would you like to add management credentials?'):
        client_id = click.prompt('Please enter your client id', type=str)
        client_secret = click.prompt('Please enter your client secret', type=str)

        set_config(config_parser, environment, 'client_id', client_id)
        set_config(config_parser, environment, 'client_secret', client_secret)

    if click.confirm('Would you like to add a security policy to your environment (you must have it enabled on your account)?'):
        app_secret = click.prompt('Please enter your application secret', type=str)
        policy = click.prompt('Please enter your application policy (type or paste as json string)', type=str)

        policy = json.loads(json.dumps(policy))
        set_config(config_parser, environment, 'app_secret', app_secret)
        set_config(config_parser, environment, 'policy', policy)

    with open(CONFIG_PATH, 'w') as file:
        config_parser.write(file)


# commands that have children commands get the Alias class
@cli.command(cls=Alias)
@click.pass_context
def manage(ctx):
    # the context (ctx) contains all the information gathered
    # by the CLI commands and can be passed to children commands

    # because manage has children commands, we add environment to current
    # command parameters so they are accessible to the children
    ctx.params['environment'] = ctx.parent.params['environment']


@manage.command()
@click.option('--name', default=None)
@click.option('--url', default=None)
@click.option('--save-to-env', type=str)
@click.pass_context
def create_app(ctx, **kwargs):

    environment = ctx.parent.params['environment']
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_PATH)

    if sys.version_info[0] < 3 and environment.lower() == 'default':
        environment = configparser.DEFAULTSECT

    client_id = config_parser.get(environment, 'client_id')
    client_secret = config_parser.get(environment, 'client_secret')

    # arguments are passed into the command functions as named
    # so we can access via kwargs without having to clutter
    # the function declaration

    save_to_env = kwargs.pop('save_to_env')
    params = {k:v for k, v in kwargs.items() if v is not None}

    response = management_utils.create_app((client_id, client_secret), params)

    if response.ok:
        app_data = response.json()
    else:
        click.echo(response.text)

    click.echo(app_data)
    # ConfigParser contains all of the config file attributes up to this point
    # so when we save, we create a new copy based on previous info and new info (if any)
    if save_to_env:

        if sys.version_info[0] < 3 and environment.lower() == 'default':
            environment = configparser.DEFAULTSECT

        try:
            set_config(config_parser, save_to_env, 'apikey', app_data['apikey'])
        except configparser.NoSectionError:
            config_parser.add_section(save_to_env)
            set_config(config_parser, save_to_env, 'apikey', app_data['apikey'])

        with  open(CONFIG_PATH, 'w') as config_file:
            config_parser.write(config_file)


@manage.command()
@click.pass_context
def list_apps(ctx):

    environment = ctx.parent.params['environment']
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_PATH)

    if sys.version_info[0] < 3 and environment.lower() == 'default':
        environment = configparser.DEFAULTSECT

    client_id = config_parser.get(environment, 'client_id')
    client_secret = config_parser.get(environment, 'client_secret')

    response = management_utils.list_apps((client_id, client_secret))

    if response.ok:
        app_data = response.json()
    else:
        click.echo(response.text)

    printer = pprint.PrettyPrinter(indent=4)
    printer.pprint(app_data)


@cli.command()
@click.option('--filename', default=None)
@click.option('--mimetype', default=None)
@click.option('--path', default=None)
@click.option('--container', default=None)
@click.option('--access', default=None)
@click.option('--base64decode', default=None)
@click.argument("files", nargs=-1)
@click.pass_context
def upload(ctx, **kwargs):
    environment = ctx.parent.params['environment']
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_PATH)

    if sys.version_info[0] < 3:
        if environment.lower() == 'default':
            environment = configparser.DEFAULTSECT

    apikey = config_parser.get(environment, 'APIKEY')
    
    try:
        app_secret = config_parser.get(environment, 'app_secret')
        policy = config_parser.get(environment, 'policy')
    except:
        app_secret = False
        policy = False

    if app_secret and policy:
        decoded_policy = json.loads(policy)
        app_security = security(decoded_policy, app_secret)
        client = Client(apikey, security=app_security)
    else:
        client = Client(apikey)
        
    files = kwargs.pop('files')
    params = {k:v for k, v in kwargs.items() if v is not None}

    if len(files) == 0:
        return click.echo("Please add filepaths for uploading")

    # iterates through file arguments. if file, uploads directly.
    # if directory, uploads all files in director
    for i in files:

        if os.path.isfile(i):
            new_filelink = client.upload(filepath=i, params=params)
            click.echo(new_filelink.url)

        elif os.path.isdir(i):
            only_files = [os.path.join(i, f) for f in os.listdir(i) if os.path.isfile(os.path.join(i, f))]

            for dir_file in only_files:
                new_filelink = client.upload(filepath=dir_file, params=params)
                click.echo(new_filelink.url)

        # presumes that isfile and isdirectory handle all valid inputs
        else:
            click.echo("{} is not a valid input".format(i))

