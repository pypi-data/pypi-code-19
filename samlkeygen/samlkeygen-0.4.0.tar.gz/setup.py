from setuptools import setup, find_packages

from samlkeygen._version import __version__

setup(
  name='samlkeygen',
  version=__version__,
  author='Mark J. Reed',
  author_email='mark.reed@turner.com',
  packages=find_packages(),
  py_modules=['samlkeygen'],
  url='http://github.com/turnerlabs/samlkeygen',
  install_requires=[
    'argh',
    'boto3',
    'bs4',
    'fasteners',
    'keyring',
    'requests',
    'requests_ntlm'
  ],
  entry_points={
    'console_scripts': [
      'samld = samlkeygen:auto_authenticate',
      'awsprof = samlkeygen:list_profiles',
      'awsprofs = samlkeygen:select_profile' 
    ]
  }
)
