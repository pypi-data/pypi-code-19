from setuptools import setup
from codecs import open
from os import path

REQUIREMENTS = [
    'django>1.5',
    'bzr>=2.5.1'
]

TEST_REQUIREMENTS = REQUIREMENTS + [
    'mocker',
    'coverage',
    'nose',
    'pep8',
]

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='django-bzrviews',
    version='0.0.2',
    description='A Bazaar View for Django Projects',
    long_description=long_description,
    url='https://launchpad.net/django-bzrviews',
    author='Canonical CE Infrastructure Team',
    author_email='ce-infrastructure@lists.canonical.com',
    license='LGPLv3',
    test_suite='bzrviews.tests',
    tests_require=TEST_REQUIREMENTS,
    packages=['bzrviews'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    ]
)
