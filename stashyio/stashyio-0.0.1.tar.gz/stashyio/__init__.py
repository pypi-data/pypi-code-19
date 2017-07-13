import os

from stashyio.stashy import Stashy

__author__ = 'Stashy.io'
__version__ = '0.0.1'

# The default Boto3 session; autoloaded when needed.
STASHY = None


def authorize(api_key=None):
    """
    Create a resource service client by name using the default session.
    """
    if api_key is None:
        api_key = os.environ.get('STASHY_AP_KEY')
        if api_key is None:
            raise Exception("STASHY_API_KEY env variable not set")
    return _get_stashy(api_key)


def setup_stashy(api_key):
    """
    Set up stashyio, passing through any parameters to the session
    constructor. There is no need to call this unless you wish to pass custom
    parameters, because a default session will be created for you.
    """
    global STASHY
    STASHY = Stashy(api_key)


def _get_stashy(api_key):
    """
    Get the stashyio object, creating one if needed.
    :rtype: :py:class:`~stashy.Stashy`
    :return: The stashyio object
    """
    if STASHY is None:
        setup_stashy(api_key)

    return STASHY
