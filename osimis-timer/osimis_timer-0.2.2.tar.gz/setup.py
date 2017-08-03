from setuptools import setup, find_packages

setup(
    name = 'osimis_timer',
    packages = find_packages(),
    version='0.2.2',  # always keep all zeroes version, it's updated by the CI script
    setup_requires=['twine', 'wheel'],
    description = 'Simple Timer/TimeOut helpers to measure elapsed time.',
    author = 'Alain Mazy',
    author_email = 'am@osimis.io',
    url = 'https://bitbucket.org/osimis/python-osimis-timer',
    keywords = ['timer', 'timeout'],
    classifiers = [],
)
