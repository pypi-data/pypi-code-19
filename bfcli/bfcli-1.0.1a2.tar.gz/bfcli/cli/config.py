import os
import json
import sys

import bitfusion
import click
import jwt

from bfcli import config
from bfcli.lib import analytics
from bfcli.lib.api import API, me

USER_PROMPT = click.option('-u',
                           '--username',
                           prompt='Enter your Bitfusion username',
                           default=lambda: config.user_config.get('username', ''))
PASS_PROMPT = click.option('-p', '--password', prompt='Enter your password', hide_input=True)

def _do_login(client, username, password):
  try:
    data = client.login(username, password)
    token = jwt.decode(data['token'], verify=False)

    analytics.set_key(client.get_segment_write_key())
    analytics.init_user(username, token)

    return data['profile']['id']
  except bitfusion.errors.AuthError as e:
    click.echo(e)
    sys.exit(1)


@click.command()
def version():
  click.echo('CLI: {}\nSDK: {}'.format(config.VERSION, bitfusion.VERSION))


@click.command()
@click.option('--host',
              prompt='What is the Bitfusion host URL?',
              default=lambda: config.user_config.get('host', ''))
@USER_PROMPT
@PASS_PROMPT
def configure(host, username, password):
  config.user_config['host'] = host
  config.user_config['username'] = username

  # Save host URL and username so user won't have to type it again
  config.store_user_config()

  # Login and get cookies
  client = bitfusion.BFApi(host=config.user_config['host'], verify=config.VERIFY_SSL)
  config.user_config['uid'] = _do_login(client, username, password)

  # Save the cookies
  config.user_config['cookies'] = client.get_cookies()

  config.store_user_config()

  click.echo('Successfully configured Bitfusion CLI\n\n' + \
             '##############################################\n' + \
             '################### CONFIG ###################\n' + \
             '##############################################\n\n' + \
             '{}'.format(json.dumps(config.user_config, indent=2)))


@click.command()
@USER_PROMPT
@PASS_PROMPT
def login(username, password):
  # Save the username
  config.user_config['username'] = username
  config.store_user_config()

  config.user_config['uid'] = _do_login(API, username, password)
  config.user_config['cookies'] = API.get_cookies()

  config.store_user_config()
  click.echo('Successfully logged in!')


@click.command()
def logout():
  analytics.track('CURRENT_USER_LOGOUT', {'ui': 'cli'})

  # Clear the cookie and save
  del config.user_config['cookies']
  config.store_user_config()

  click.echo('Successfully logged out.')
