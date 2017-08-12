import os

# see if work directory has been defined and is useable
if 'BEATBOX_WORK_PATH' in os.environ.keys():
    try:
        if not os.path.isdir(os.environ['BEATBOX_WORK_PATH']):
            os.makedirs(os.environ['BEATBOX_WORK_PATH'])
    except:
        raise Exception("Could not create working directory " + os.environ['BEATBOX_WORK_PATH'])
else:
    raise Exception('BEATBOX_WORK_PATH not found in environment - set it to a path were BEATBOX can write stuff to.')

# see if archive directory has been defined and is useable
if 'BEATBOX_ARCHIVE_PATH' in os.environ.keys():
    try:
        if not os.path.isdir(os.environ['BEATBOX_ARCHIVE_PATH']):
            os.makedirs(os.environ['BEATBOX_ARCHIVE_PATH'])
    except:
        raise Exception("Could not create archive directory " + os.environ['BEATBOX_ARCHIVE_PATH'])
else:
    raise Exception('BEATBOX_ARCHIVE_PATH not found in environment - set it to a path were BEATBOX can write stuff to.')

from . import helpers
from . import cycling
try:
    import matplotlib
    from . import plotting
except:
    import warnings
    warnings.warn('matplotlib not found - plotting disabled.')

from . import multimox
from beatbox import run

import _console
