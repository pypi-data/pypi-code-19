import sys
import os
import click

import analytics
import bitfusion

from bfcli import config

VERIFY_SSL = False if os.environ.get('VERIFY_SSL', '').lower() == 'false' else True
API = bitfusion.BFApi(host=config.conf.get('host'), cookies=config.conf.get('cookies'), verify=VERIFY_SSL)
analytics.write_key = API.get_segment_write_key()

def me():
  return API.User.get(config.conf['uid'])

def api_error_decorator(handler):
  def api_error_wrapper(*args, **kwargs):
    try:
      return handler(*args, **kwargs)
    except bitfusion.errors.AuthError as e:
      click.echo('You must run `{} login` again'.format(config.CMD))
      sys.exit(1)

  return api_error_wrapper


def enable_api_decorator():
  API._session._handle_response = api_error_decorator(
    API._session._handle_response
  )
