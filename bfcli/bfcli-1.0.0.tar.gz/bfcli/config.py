import json
import os
import sys

import click
import jsonschema
import yaml

from bfcli.command import CMD
from bfcli.version import VERSION

conf = {}
config_file_path = os.path.expanduser('~/.bfcli.conf')

config_schema = """
type: object

required:
  - host
  - uid
  - username

properties:
  host:
    type: string
    pattern: "^http(s)?://"
  username:
    type: string
  uid:
    type: string
  cookies:
    type: object
"""

try:
  with open(config_file_path, 'r') as f:
    # This returns None if the file is empty
    conf = yaml.load(f)
except:
  pass
finally:
  if not conf:
    conf = {}


def ensure_config_is_valid():
  try:
    validate_config()
  except Exception as e:
    click.echo('Bitfusion CLI is not configured properly. Please run `{} config`'.format(CMD))
    sys.exit(1)


def validate_config(config=conf):
  return jsonschema.validate(config, yaml.load(config_schema))


def save_config(**kwargs):
  config = yaml.load(json.dumps(kwargs))

  with open(config_file_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
