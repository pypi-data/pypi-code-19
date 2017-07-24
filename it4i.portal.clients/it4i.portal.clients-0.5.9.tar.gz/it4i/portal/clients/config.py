import ConfigParser
import os
import sys
import re

from logger import LOGGER

default_config_path = '/usr/local/etc/it4i-portal-clients/main.cfg'
local_config_path = os.path.expanduser('~/.it4ifree')

config = ConfigParser.ConfigParser()
config_files = '\n'.join((4*' ' + default_config_path,
                          4*' ' + local_config_path))

try:
    config.readfp(open(default_config_path))
except IOError:
    LOGGER.warning("Default config file %s not found", default_config_path)
    if not config.read(local_config_path):
        LOGGER.error("Tried (in the following order), but no configuration found:\n%s",
                     config_files)
        sys.exit(1)

if not config.read(local_config_path):
    LOGGER.info("Local config file %s not found", local_config_path)

# mandatory configuration options
api_url = "https://scs.it4i.cz/api/v1/"
api_url_optname = "api_url"
try:
    api_url = config.get("main", api_url_optname)
    1/len(api_url)
except:
    pass

api_url = re.sub('\/$', '', api_url)

it4ifreetoken = None
it4ifreetoken_optname = "it4ifreetoken"
try:
    it4ifreetoken = config.get("main", it4ifreetoken_optname)
    1/len(it4ifreetoken)
except:
    LOGGER.error("""Missing or unset configuration option: %s

Suggested paths:
%s
""", it4ifreetoken_optname, config_files)
    sys.exit(1)
