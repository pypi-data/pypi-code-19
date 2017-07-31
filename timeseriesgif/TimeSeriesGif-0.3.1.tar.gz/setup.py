from distutils.core import setup
setup(
  name = 'TimeSeriesGif',
  packages = ['TimeSeriesGif'],
  version = '0.3.1',
  description = 'Create gifs from pandas time series.',
  author = 'Andrew Han',
  author_email = 'handrew11@gmail.com',
  url = 'https://github.com/handrew/TimeSeriesGif', 
  download_url = 'https://github.com/handrew/TimeSeriesGif/archive/0.3.1.tar.gz', 
  keywords = ['time series', 'pandas', 'visualization'], 
  install_requires=['numpy', 'pandas', 'matplotlib', 'imageio'],
  classifiers = []
)