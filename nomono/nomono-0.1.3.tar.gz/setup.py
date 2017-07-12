import os

from pip.req import parse_requirements
from setuptools import find_packages, setup
from setuptools import setup, find_packages
from distutils.util import convert_path

# ========================================
# Parse requirements for all configuration
# ========================================
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(filename=os.path.join('.', 'requirements.txt'), session='update')
# # reqs is a list of requirement
# # e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

SOLUTION_NAME = 'wonderjam'

# ========================================
# Readme
# ========================================
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
# ========================================
# Version parsing
# ========================================
main_ns = {}
ver_path = convert_path('nboot/version.py')
with open(ver_path) as ver_file:
    exec (ver_file.read(), main_ns)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(

    name='nomono',
    version=main_ns['__version__'],
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0 License',  # example license
    description='Nomono web scraper and comparison tool.',
    long_description=README,
    url='https://github.com/lordoftheflies/nomono/',
    author='lordoftheflies',
    author_email='laszlo.hegedus@cherubits.hu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: System :: Monitoring',
        'Development Status :: 2 - Pre-Alpha'
    ],
    install_requires=reqs,
    private_repository="https://pypi.cherubits.hu",
    # tests_require=[
    # ],
    # test_suite="assetadapter.tests",
    # entry_points={
    #     'console_scripts': [
    #         'hedgehog-sc-scheduler = orchestrator.celery:main',
    #         'hedgehog-sc-orchestrator = assetadapter.main:main',
    #     ]
    # }
)
