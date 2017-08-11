from distutils.core import setup
setup(
  name = 'fuser',
  packages = ['fuser'], # this must be the same as the name above
  version = '0.9',
  description = 'A library to handle user related tasks in Flask',
  author = 'Patrick Allen',
  author_email = 'patrickgallen@gmail.com',
  url = 'https://github.com/pgallen90/fuser',
  download_url = 'https://github.com/pgallen90/fuser/archive/0.9.tar.gz',
  keywords = ['flask', 'auth', 'password', 'login', 'dashboard'], 
  classifiers = [],
  include_package_data=True,
)
