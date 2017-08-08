from distutils.core import setup
setup(
  name = 'oglhslack',
  packages = ['oglhslack'],
  version = '0.1.2',
  description = 'A Slack bot client for Lighthouse API',
  author = 'Lighthouse Team',
  author_email = 'engineering@opengear.com',
  url = 'https://github.com/thiagolcmelo/oglhslack',
  download_url = 'https://github.com/thiagolcmelo/oglhslack/archive/0.1.0.tar.gz',
  keywords = ['api', 'opengear', 'lighthouse', 'slackbot'],
  classifiers = [],
  install_requires = ['pyyaml', 'slackclient', 'oglhclient']
)
