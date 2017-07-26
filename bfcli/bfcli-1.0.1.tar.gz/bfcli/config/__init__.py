import os
import sys

import click
from decorator import decorator

from bfcli.command import CMD
from bfcli.config import local_file
from bfcli.version import VERSION

def store_user_config():
  local_file.save_config(user_config)

@decorator
def validate_config(f, *args, **kwargs):
  try:
    local_file.validate_config(user_config)
  except:
    click.echo('Invalid config file. You must run `{} configure`'.format(CMD))
    sys.exit(1)
  
  return f(*args, **kwargs)

user_config = local_file.read_config()
VERIFY_SSL = False if os.environ.get('BF_VERIFY_SSL', '').lower() == 'false' else True
