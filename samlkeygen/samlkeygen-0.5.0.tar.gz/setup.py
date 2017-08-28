from setuptools import setup, find_packages
import os, sys

setup(
  name='samlkeygen',
  version=os.popen('{} samlkeygen/_version.py'.format(sys.executable)).read().rstrip(),
  author='Mark J. Reed',
  author_email='mark.reed@turner.com',
  packages=find_packages(),
  py_modules=['samlkeygen'],
  url='http://github.com/turnerlabs/samlkeygen',
  install_requires=open('requirements.txt','r').read().splitlines(),
  entry_points={
    'console_scripts': [
      'samld = samlkeygen:auto_authenticate',
      'awsprof = samlkeygen:list_profiles',
      'awsprofs = samlkeygen:select_profile' 
    ]
  }
)
