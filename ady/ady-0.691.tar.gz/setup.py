from distutils.core import setup

setup(
  name = 'ady',
  packages = ['ady'],
  version = '0.691',
  description = 'ADY - Schedule between Baku Sumgait Baku',
  author = 'Chingiz Huseynzade',
  author_email = 'chingiz.h@gmail.com',
  license='MIT',
  url = 'https://github.com/Chingiz/ADY-Hereket-Cedveli',
  download_url = 'https://github.com/Chingiz/ADY-Hereket-Cedveli/archive/0.691.tar.gz',
  keywords = ['ady', 'schedule', 'baku', 'sumgait'],
  scripts=['bin/ady'],
  install_requires=['humanfriendly', 'fabulous', 'bs4', 'BeautifulSoup', 'requests', 'urllib3']
)