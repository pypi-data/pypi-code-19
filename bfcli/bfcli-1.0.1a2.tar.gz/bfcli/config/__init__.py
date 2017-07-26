import os

from bfcli.command import CMD
from bfcli.config import local_file
from bfcli.version import VERSION

def store_user_config():
  local_file.save_config(user_config)


user_config = local_file.read_config()
VERIFY_SSL = False if os.environ.get('BF_VERIFY_SSL', '').lower() == 'false' else True
