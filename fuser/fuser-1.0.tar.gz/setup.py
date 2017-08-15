from distutils.core import setup
setup(
  name = 'fuser',
  packages = ['fuser', 'fuser/templates'], # this must be the same as the name above
  version = '1.0',
  description = 'A library to handle user related tasks in Flask',
  author = 'Patrick Allen',
  data_files=[('fuser/templates', 
              ['fuser/templates/fuser_default_login.html', 
              'fuser/templates/fuser_default_set_pw.html',
              'fuser/templates/fuser_set_password.html',
              'fuser/templates/request_password_change.html']),
              ],
  author_email = 'patrickgallen@gmail.com',
  url = 'https://github.com/pgallen90/fuser',
  download_url = 'https://github.com/pgallen90/fuser/archive/0.9.3.tar.gz',
  keywords = ['flask', 'auth', 'password', 'login', 'dashboard'], 
  classifiers = [],
  include_package_data=True,
)
