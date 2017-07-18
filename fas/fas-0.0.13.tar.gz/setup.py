import os
import codecs
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

# notes at:
# http://peterdowns.com/posts/first-time-with-pypi.html

setup(
    name='fas',
    version="0.0.13",
    url='',
    author='Omer Duskin',
    author_email='dusking@gmail.com',
    license='LICENSE',
    platforms='All',
    description='FaaSpot Client',
    long_description=read('README.rst'),
    py_modules=['fas'],
    entry_points={'console_scripts': ['fas = fas.main:main']},
    packages=[
        'fas',
        'fas.cli',
        'fas.client',
        'fas.commands',
        'fas.commands.samples',
    ],
    package_data={
        'fas': [
            'VERSION'
        ]
    },
    install_requires=[
        "prettytable==0.7.2",
        'PyYAML==3.10',
        'requests==2.7.0',
        'retrying==1.3.3',
        'future==0.16.0',
        'six==1.10.0'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
