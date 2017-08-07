from __future__ import absolute_import
import logging

from .config import get_config
from .version import version

from path import Path

__version__ = version

CONFIG = get_config()
PRMS_DIR = Path(CONFIG['prms_dir'])

logging.getLogger(__name__).addHandler(logging.NullHandler())
