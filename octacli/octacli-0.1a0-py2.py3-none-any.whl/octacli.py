#!/usr/bin/python
import click
import requests
import configparser
import base64
from os import path
import namespace as ns
import user
import service
import policy
import alert
from tokens import token_file_path

properties_file_path = path.expanduser('~/.octarine_login')


@click.group()
@click.option('--port', default=8080)
@click.pass_context
def octacli(ctx, port):
    ctx.obj={}
    config = configparser.ConfigParser()
    config.read(properties_file_path)
    if 'Credentials' in config.sections():
        ctx.obj['creds'] = config['Credentials']
        print(ctx.obj['creds']['Server'])
    ctx.obj['port'] = port


@octacli.command()
@click.option('--namespace')
@click.option('--server')
@click.option('--username')
@click.option('--password', prompt=True, hide_input=True)
@click.pass_context
def login(ctx, namespace, server, username, password):
    if 'creds' not in ctx.obj:
        if not namespace or not username:
            click.echo('No credentials file found. Please provide namespace and username')
            return
        if not server:
            server = 'localhost'
    if not namespace:
        namespace = ctx.obj['creds']['Namespace']
    if not username:
        username = ctx.obj['creds']['Username']
    if not server:
        server = ctx.obj['creds']['Server']
    if namespace == 'octarine':
        password += '\n'
    authenticate(server, ctx.obj['port'], namespace, username, password)


def authenticate(server, port, namespace, username, password):
    click.echo('logging in %s:%s:%s:%s' % (server, namespace, username, password))
    try:
        req = requests.post('http://{}:{}/ns/{}/login'.format(server, port, namespace),
                            json={'name': username,
                                  'password': base64.b64encode(password.encode()).decode()})
    except requests.exceptions.ConnectionError as ex:
        print(ex)
        return
    if req.status_code != 200:
        click.echo('login failed: %s' % req.text)
        return
    with open(token_file_path, 'w') as token_file:
        token_file.write(req.text)
    config = configparser.ConfigParser()
    config['Credentials'] = {'Server': server, 'Port': port, 'Namespace': namespace, 'Username': username}
    with open(properties_file_path, 'w') as props_file:
        config.write(props_file)

#if __name__ == '__main__':
octacli.add_command(ns.namespace)
octacli.add_command(user.user)
octacli.add_command(service.service)
octacli.add_command(policy.rule)
octacli.add_command(alert.alert)
#octacli(obj={})
