import os
import sys

# Add the vendors path to sys.path
current_dir = os.path.abspath(os.path.dirname(__file__))


def install_vendors():
    """ Add current directory to sys.path for importing from vendors as
    a fallback.
    Be aware that our vendors comes last as a fallback. An incompatible version
    could be loaded instead.
    """
    sys.path.append(current_dir)
