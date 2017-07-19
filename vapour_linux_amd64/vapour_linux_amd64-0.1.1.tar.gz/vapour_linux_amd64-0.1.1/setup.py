from setuptools import setup
import sys

if len(sys.argv) > 1:
    data = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]

setup(
    name=data,
    packages=[data],
    package_data={
        data: ['*.zip']
    },
    version='0.1.1',
    description='This package contains binary executable dependencies for the master.',
    include_package_data=True
)
