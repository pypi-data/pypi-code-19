# -*- coding: utf-8 -*-
import logging
import os
import sys

from lore import env, util
from lore.env import root
from lore.ansi import underline
from os.path import isfile, join

logger = logging.getLogger(__name__)

if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    ModuleNotFoundError = ImportError

if env.launched():
    os.chdir(root)
    
    try:
        import rollbar
        rollbar.init(
            os.environ.get("ROLLBAR_ACCESS_TOKEN", None),
            allow_logging_basic_config=False,
            environment=env.name,
            enabled=(env.name != env.DEVELOPMENT),
            handler='blocking',
            locals={"enabled": True})

        def report_error(exc_type, value, tb):
            import traceback
            logger.critical('Exception: %s' % ''.join(
                traceback.format_exception(exc_type, value, tb)))
            rollbar.report_exc_info((exc_type, value, tb))
    
        sys.excepthook = report_error
    except ModuleNotFoundError as e:
        pass

    try:
        import numpy
        numpy.random.seed(1)
        logger.debug('numpy.random.seed(1)')
    except ModuleNotFoundError as e:
        pass
    
    # Deprecation warnings
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
__version__ = '0.1.12'
__maintainer__ = 'Montana Low'
__email__ = 'montana@instacart.com'
__status__ = 'Prototype'
