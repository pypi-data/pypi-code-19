from setuptools import setup, find_packages

from hudai import __version__

HOMEPAGE = 'https://github.com/FoundryAI/hud-ai-python'

setup(
  name = 'hudai',
  packages = find_packages(),
  version = __version__,
  description = 'HUD.ai python bindings',
  author = 'HUD.ai Engineering',
  author_email = 'engineering@hud.ai',
  license='MIT',
  url = HOMEPAGE,
  download_url = '{}/releases/{}.tar.gz'.format(HOMEPAGE, __version__),
  keywords = ['hudai', 'foundry.ai', 'foundrydc'], # arbitrary keywords
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
