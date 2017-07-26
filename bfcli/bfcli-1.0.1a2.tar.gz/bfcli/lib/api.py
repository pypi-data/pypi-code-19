import sys
import os

import bitfusion
import click
from decorator import decorator

from bfcli import config
from bfcli.lib import analytics

API = bitfusion.BFApi(host=config.user_config.get('host'),
                      cookies=config.user_config.get('cookies'),
                      verify=config.VERIFY_SSL)

analytics.set_key(API.get_segment_write_key())

def me():
  return API.User.get(config.user_config['uid'])


@decorator
def auth_error_handler(f, *args, **kwargs):
  try:
    return f(*args, **kwargs)
  except bitfusion.errors.AuthError as e:
    click.echo('You must run `{} login` again'.format(config.CMD))
    sys.exit(1)
