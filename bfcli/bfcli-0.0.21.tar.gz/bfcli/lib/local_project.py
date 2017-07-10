import os

from bfcli.lib.api import API

PROJECT_FILE = '.flex'

def path():
  work_dir = os.getcwd()
  return os.path.join(work_dir, PROJECT_FILE)


def exists():
  if os.path.isfile(path()):
    return True

  return False


def json():
  import json as _json
  with open(path()) as _f:
    return _json.load(_f)


def get():
  p_json = json()
  return API.Project.get(p_json['id'])


def remove():
  os.remove(path())
