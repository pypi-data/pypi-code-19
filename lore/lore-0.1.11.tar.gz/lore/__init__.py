# -*- coding: utf-8 -*-
import logging
import os

from lore import env, util
from lore.env import root
from lore.ansi import underline
from os.path import isfile, join

logger = logging.getLogger(__name__)

if env.launched():
    os.chdir(root)
    
    if isfile(join(root, '.python-version')):
        logger.warning(
            underline('.python-version') + ' is deprecated in favor of ' +
            underline('runtime.txt') + ' to avoid conflicts with pyenv, and ' +
            'add support for heroku buildpacks.'
        )

elif not env.exists():
    logger.error(
        'Could not find lore env. Missing ' + underline('runtime.txt')
    )

__author__ = 'Montana Low and Jeremy Stanley'
__copyright__ = 'Copyright © 2017, Instacart'
__credits__ = ['Montana Low', 'Jeremy Stanley']
__license__ = 'MIT'
__version__ = '0.1.11'
__maintainer__ = 'Montana Low'
__email__ = 'montana@instacart.com'
__status__ = 'Prototype'
