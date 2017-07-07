import os
from appdirs import *
app_dirs = AppDirs("podcast-dl", "podcast-dl")
DBFILE = os.path.join(app_dirs.user_data_dir, 'podcast-dl.db')
LOGFILE = os.path.join(app_dirs.user_log_dir, 'podcast-dl.log')

class Config():
  def __init__(self):
    pass

  @classmethod
  def context(self):
    return dict(help_option_names=['-h', '--help'])

  @classmethod
  def validate(self):
    files = [
      DBFILE,
      LOGFILE
    ]

    directories = [
      app_dirs.user_data_dir,
      app_dirs.user_log_dir,
      app_dirs.user_cache_dir
    ]

    for directory in directories:
      if not os.path.isdir(directory):
        try:
          os.makedirs(directory)
        except OSError as e:
          print(e)
          return

    for file in files:
      if not os.path.isfile(file):
        try:
          open(file, 'w+')
        except OSError as e:
          print(e)
          return

    return True

  @classmethod
  def logfile(self):
    import logging
    logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
    return logging.getLogger(__name__)