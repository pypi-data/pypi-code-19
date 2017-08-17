from distutils.core import setup
setup(
  name = 'scenechange',
  packages = ['scenechange'], # this must be the same as the name above
  version = '0.1',
  description = 'Insert chapter markers for scene changes using Matroska using ffmpeg and mkvpropedit',
  author = 'Kieran O\'Leary',
  author_email = 'kieran.o.leary@gmail.com',
  url = 'https://github.com/kieranjol/scenechange', # use the URL to the github repo
  download_url = 'https://github.com/kieranjol/scenechange/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['ffmpeg', 'mkvpropedit', 'metadata', 'scene detect', 'scene change'], # arbitrary keywords
  classifiers = [],
)
