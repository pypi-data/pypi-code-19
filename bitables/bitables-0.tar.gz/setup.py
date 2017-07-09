__author__ = 'Nathan L. Conrad'
__copyright__ = 'Copyright 2017 Nathan L. Conrad'

from setuptools import find_packages, setup

def _main():
    setup(
        name='bitables',
        version=0,
        author=__author__,
        author_email='nathan@noreply.alt-teknik.com',
        url='https://alt-teknik.com',
        packages=find_packages()
        )

if __name__ == '__main__':
    _main()
