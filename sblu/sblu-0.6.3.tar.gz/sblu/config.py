import os
import getpass
from configobj import ConfigObj

from path import Path

DEFAULTS = {
    "cluspro": {
        "local_path": None,
        "username": None,
        "api_secret": None,
        "server": "cluspro.bu.edu"
    },
    "ftmap": {
        "local_path": None,
        "username": None,
        "api_secret": None,
        "server": "ftmap.bu.edu"
    },
    "prms_dir": os.path.join(os.environ['HOME'], "prms")
}


def get_config(config_path="~/.sblurc"):
    config = ConfigObj(DEFAULTS)

    config_file = Path(config_path).expand()
    config.filename = config_file

    if config_file.exists():
        config.merge(ConfigObj(config_file))
    else:
        config.write()

    return config
