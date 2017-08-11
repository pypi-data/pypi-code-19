from distutils.core import setup
setup(
  name = 'bootstraps',
  packages = ['bootstraps', 'bootstraps/macros'], # this must be the same as the name above
  version = '0.9.3',
  description = 'A library to handle user related tasks in Flask',
  author = 'Patrick Allen',
  author_email = 'patrickgallen@gmail.com',
  url = 'https://github.com/pgallen90/bootstraps',
  download_url = 'https://github.com/pgallen90/bootstraps/archive/0.9.3.tar.gz',
  keywords = ['bootstrap', 'flask', 'forms'], 
  classifiers = [],
  include_package_data=True,
)
