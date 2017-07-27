#!/usr/bin/python2
#
from setuptools import setup
import io

with io.open('README.rst', 'rt', encoding='utf-8') as f:
    readme_contents = f.read()

setup_args = dict(
    name = "pytest-modifyjunit",
    version = "1.1",
    description = "Utility for adding additional properties to junit xml for IDM QE",
    long_description = readme_contents,
    license = "GPL",
    author = "Scott Poore, Niranjan M.R",
    author_email = "spoore@redhat.com, mrniranjan@fedoraproject.org",
    packages = ["pytest_modifyjunit"],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['pytest>=2.4.0'],  # (paramiko & PyYAML are suggested)
    entry_points = {
        'pytest11': [
            'modifyjunit = pytest_modifyjunit.plugin',
        ],
    },
)
if __name__ == '__main__':
    setup(**setup_args)
