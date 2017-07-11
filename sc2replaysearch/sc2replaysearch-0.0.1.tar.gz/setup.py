from distutils.core import setup

VERSION = '0.0.1'

setup(
  name='sc2replaysearch',
  packages=['sc2replaysearch'],
  version=VERSION,
  description='Utility for finding the most recently created SC2 replay',
  author='Hugo Wainwright',
  author_email='wainwrighthugo@gmail.com',
  url='https://github.com/frugs/sc2replaysearch',
  download_url='https://github.com/frugs/sc2replaysearch/tarball/' + VERSION,
  keywords=['sc2', 'replay'],
  classifiers=[],
)
