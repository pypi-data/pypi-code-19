"""
Logging facilities.
"""

import logging
from .pkginfo import __title__

#: The logging object.
log = logging.getLogger(__title__)

# Add a null handler.
log.addHandler(logging.NullHandler())


def init_logging(verbose=False, formatstring=None):
    # Add a stderr handler.
    handler = logging.StreamHandler()
    log.addHandler(handler)

    # Set the log message format.
    if not formatstring:
        formatstring = "%(name)s: %(levelname)s: %(message)s"

    formatter = logging.Formatter(formatstring)
    handler.setFormatter(formatter)

    # Set log level.
    log.setLevel(logging.INFO if verbose else logging.WARNING)
