from distutils.core import setup

VERSION = "0.0.13"

setup(
  name='techlabreactor',
  packages=['techlabreactor'],
  version=VERSION,
  description='Utility for performing replay analysis of SC2 replays',
  author='Hugo Wainwright',
  author_email='wainwrighthugo@gmail.com',
  url='https://github.com/frugs/techlab-reactor',
  download_url='https://github.com/frugs/techlab-reactor/tarball/' + VERSION,
  keywords=['sc2', 'replay', 'sc2reader'],
  classifiers=[],
)
