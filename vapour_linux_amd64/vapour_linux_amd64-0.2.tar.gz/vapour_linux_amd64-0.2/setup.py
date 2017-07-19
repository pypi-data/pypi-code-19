from setuptools import setup
import sys

if len(sys.argv) > 1:
    pkg,ver = sys.argv[1].split(':')
    sys.argv = [sys.argv[0]] + sys.argv[2:]

setup(
    name=pkg,
    packages=[pkg],
    package_data={
        pkg: ['*.zip']
    },
    version=ver,
    description='This package contains binary executable dependencies for the master.',
    author='VapourApps',
    author_email='vapour@vapour.com'
)
