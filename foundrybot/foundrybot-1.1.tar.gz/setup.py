from setuptools import setup, find_packages
setup(
  name = 'foundrybot',
  packages = ['foundrybot', 'foundrybot/resources'], # this must be the same as the name above
  version = '1.1',
  description = 'Foundrybot python bindings',
  author = 'Nick Gerner',
  author_email = 'nick@foundry.ai',
  url = 'https://github.com/FoundryAI/foundrybot-python', # use the URL to the github repo
  download_url = 'https://github.com/FoundryAI/foundrybot-python/archive/1.0.tar.gz',
  keywords = ['foundrybot', 'foundry.ai', 'foundrydc'], # arbitrary keywords
  classifiers = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7'
  ],
  install_requires=[
    'requests',
    'pydash'
  ]
)