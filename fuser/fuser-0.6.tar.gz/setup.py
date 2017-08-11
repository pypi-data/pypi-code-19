from distutils.core import setup
setup(
  name = 'fuser',
  packages = ['fuser', 'fuser/templates'], # this must be the same as the name above
  version = '0.6',
  description = 'A library to handle user related tasks in Flask',
  author = 'Patrick Allen',
  author_email = 'patrickgallen@gmail.com',
  url = 'https://github.com/pgallen90/fuser',
  download_url = 'https://github.com/pgallen90/fuser/archive/0.6.tar.gz',
  keywords = ['flask', 'auth', 'password', 'login', 'dashboard'], 
  classifiers = [],
)
