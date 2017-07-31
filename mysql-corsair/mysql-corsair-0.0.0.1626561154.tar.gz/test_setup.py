# -*- coding: utf-8 -*-
from setuptools import setup
from HTMLParser import HTMLParser
import sys
import urllib2
from random import randint


class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        try:
            self.versions
        except:
            self.versions = []
        if 'corsair' in data:
            self.versions.append(data)


class VersionNumber:
    def __init__(self, version_string):
        split_string = version_string.split(".")
        if len(split_string) != 3:
            self.major_version = self.minor_version = self.build_version = 0
        try:
            self.major_version = int(split_string[0])
            self.minor_version = int(split_string[1])
            self.build_version = int(split_string[2])
        except ValueError:
            self.major_version = self.minor_version = self.build_version = 0

    def to_string(self):
        return "{0}.{1}.{2}".format(
            self.major_version,
            self.minor_version,
            self.build_version
        )



pypi = 'pypi'


def add_one_to_version(version):
    version = version.to_string()
    if 'bdist_wheel' in sys.argv:
        return version
    split_version = version.split(".")
    # 0.0.13 -> ['0', '0', '13']
    new_int = int(split_version[-1]) + 1
    return '.'.join(
        split_version[:-1] + [str(new_int)]
    )


def get_most_recent_version(package_name, pypi):
    package_info = get_package_info(package_name, pypi)
    version_number_strings = get_version_number_strings(
        package_info, package_name, pypi
    )
    version_numbers = []

    for version_number_string in version_number_strings:
        version_numbers.append(VersionNumber(version_number_string))

    sorted_version_numbers = sorted(
        version_numbers, 
        key=lambda version_number: (
            version_number.major_version,
            version_number.minor_version,
            version_number.build_version
        )
    )
    most_recent_version = sorted_version_numbers[-1]
    return most_recent_version


def get_package_info(package, pypi):
    pypi_base_url = 'https://{0}.python.org'.format(pypi)
    pypi_simple_base_url = '{0}/simple'.format(pypi_base_url)

    package_url = "{0}/{1}".format(pypi_simple_base_url, package)

    r = urllib2.urlopen(package_url)
    if r.getcode() != 200:
        raise Exception("Cannot get the url {0}.".format(package_url))

    return r.read()


def get_version_number_strings(package_info, package_name, pypi):
    version_number_strings = []
    package_info = get_package_info(package_name, pypi)


    parser = MyHTMLParser()
    parser.feed(package_info)

    versions = parser.versions

    start_index = len(package_name) + 1
    end_index = len('.tar.gz')
    for i in versions:
        version_number_strings.append(
            i[start_index:(len(i)-end_index)]
        )
    return version_number_strings


setup(
    author="Andre Kuney",
    author_email="andre.kuney@newsela.com",
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Database',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    description="Tool to move slices of data from one MySQL store to another",
    entry_points={
        "console_scripts": ['mysql-corsair = MySQLCorsair.main:main']
    },
    install_requires=[
        "mysqlclient==1.3.7",
        "networkx==1.11",
    ],
    name="mysql-corsair",
    packages=[
        "MySQLCorsair", "MySQLCorsair.data_slices"
    ],
    url='https://github.com/newsela/mysql-corsair',
    version='0.0.0.{0}'.format(randint(1000000000, 2000000000))
)

