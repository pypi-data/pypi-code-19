from distutils.core import setup
setup(
  name = 'bootstraps',
  packages = ['bootstraps', 'bootstraps/macros'], # this must be the same as the name above
  version = '1.0',
  description = 'A library to handle user related tasks in Flask',
  author = 'Patrick Allen',
  data_files=[('bootstraps/macros', 
              ['bootstraps/macros/_form_macros.html', 
              'bootstraps/macros/_navbars.html']),
              ],
  author_email = 'patrickgallen@gmail.com',
  url = 'https://github.com/pgallen90/bootstraps',
  download_url = 'https://github.com/pgallen90/bootstraps/archive/0.9.3.tar.gz',
  keywords = ['bootstrap', 'flask', 'forms'], 
  classifiers = [],
  include_package_data=True,
)
