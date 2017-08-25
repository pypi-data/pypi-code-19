import os
from setuptools import find_packages, setup

requirements = [
    'paramiko',
    'requests',
    'ansicolors',
    'progressbar2',
    'termcolor',
    'colorama',
]

if os.name == 'posix':
    requirements.append('sh')

print find_packages()

setup(name="mcommons",
    install_requires=requirements,
    version= "0.1",
    description="Some common utility methods I use often",
    author="Moshe Immerman",
    author_email='name.surname@gmail.com',
    platforms=["any"],
    license="BSD",
    url="http://github.com/Moshe-Immerman/python-commons",
    packages=['commons']
)
