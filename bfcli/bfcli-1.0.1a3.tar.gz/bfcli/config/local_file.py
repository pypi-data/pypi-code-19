import errno
import json
import os

import jsonschema
import yaml

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


def read_config():
  conf = None
  try:
    with open(config_file_path, 'r') as f:
      # This returns None if the file is empty
      conf = yaml.load(f)
  except (OSError, IOError) as e:
    if getattr(e, 'errno', 0) != errno.ENOENT:
      raise e

  if not conf:
    conf = {}

  return conf


def validate_config(config):
  return jsonschema.validate(config, yaml.load(config_schema))


def save_config(new_config):
  config = yaml.load(json.dumps(new_config))

  with open(config_file_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
