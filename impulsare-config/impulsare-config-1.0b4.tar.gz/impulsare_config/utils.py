import os
from distutils.sysconfig import get_config_vars


def get_venv_basedir():
    """Returns the base directory of the virtualenv, useful to read configuration and plugins"""

    try:
        import virtualenv
        raise EnvironmentError("You must be in a virtual environment")
    except Exception:
        return os.path.abspath(get_config_vars()['exec_prefix'] + '/../')
