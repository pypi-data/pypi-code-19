from distutils.core import setup
setup(
  name = 'graphite-analytics',
  packages = ['graphite'],
  version = '0.1.2.5',
  description = 'Create a print-out template for your google analytics data',
  author = 'Arian Moslem',
  author_email = 'amoslem678@gmail.com',
  url = 'https://github.com/ARM-open/Graphite',
  keywords = ['Google analytics', 'analytics', 'templates'], 
  classifiers = [],
  install_requires=['Click', 'google-api-python-client', 'jinja2'],
  entry_points={'console_scripts': [
    'graphite-analytics = graphite.graphite:main'
  ]},
  package_data={'graphite': ['*.txt', 'graphite/capture.js', 'graphite/templates/css/styles.css', 'graphite/templates/js/Chart.PieceLabel.js', 'graphite/templates/images/Calendar-icon.png', 'graphite/templates/html/render.html', 'graphite/templates/fonts/Antro_Vectra.otf', 'README.md', 'graphite.3']},
  include_package_data=True
)