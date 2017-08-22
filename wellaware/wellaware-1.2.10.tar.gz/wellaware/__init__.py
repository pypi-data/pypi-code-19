import os

__wellaware_version_path__ = os.path.realpath(__file__ + '/../VERSION')
__version__ = open(__wellaware_version_path__, 'r').readline().strip()
