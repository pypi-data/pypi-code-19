# -*- coding: utf-8 -*-
import logging
import os
import sys
import atexit

from lore import env, util, ansi
from lore.env import root
from lore.ansi import underline
from os.path import isfile, join

logger = logging.getLogger(__name__)

if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    ModuleNotFoundError = ImportError


__author__ = 'Montana Low and Jeremy Stanley'
__copyright__ = 'Copyright © 2017, Instacart'
__credits__ = ['Montana Low', 'Jeremy Stanley']
__license__ = 'MIT'
__version__ = '0.1.18'
__maintainer__ = 'Montana Low'
__email__ = 'montana@instacart.com'
__status__ = 'Prototype'


def banner():
    import socket
    import getpass
    
    return '%s in %s on %s' % (
        ansi.foreground(ansi.GREEN, env.project),
        ansi.foreground(env.color, env.name),
        ansi.foreground(ansi.CYAN,
                        getpass.getuser() + '@' + socket.gethostname())
    )


if env.launched():
    os.chdir(root)

    logger.info(banner())
    logger.debug('python environment: %s' % env.prefix)

    if isfile(join(root, '.python-version')):
        logger.warning(
            underline('.python-version') + ' is deprecated in favor of ' +
            underline('runtime.txt') + ' to avoid conflicts with pyenv, and ' +
            'add support for heroku buildpacks.'
        )

    try:
        import numpy
    
        numpy.random.seed(1)
        logger.debug('numpy.random.seed(1)')
    except ModuleNotFoundError as e:
        pass

    try:
        import keras
    
        def cleanup_tensorflow():
            # prevents random gc exception at exit
            keras.backend.clear_session()
        
        atexit.register(cleanup_tensorflow)
    except ModuleNotFoundError as e:
        pass

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

elif not env.exists():
    logger.error(
        'Could not find lore env. Missing ' + underline('runtime.txt')
    )
