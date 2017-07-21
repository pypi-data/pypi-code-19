"""Installer for trequests
"""

from os import path
try:
        from setuptools import setup, find_packages
except ImportError:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup, find_packages


cwd = path.dirname(__file__)
__version__ = open(path.join(cwd, 'trequests/trequests_version.txt'),
                   'r').read().strip()

setup(
    name='trequests_xsren',
    description='A Tornado async HTTP/HTTPS client '
                'adaptor for python-requests. Forked from https://github.com/1stvamp/trequests .',
    long_description=open('README.rst').read(),
    version=__version__,
    author='xsren',
    author_email='bestrenxs@gmail.com',
    url='https://github.com/xsren/trequests',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=open('requirements.txt').readlines(),
    package_data={'': ['trequests_version.txt']},
    include_package_data=True,
    test_suite="trequests_tests",
    license='BSD'
)
