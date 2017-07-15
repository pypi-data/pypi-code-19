from setuptools import setup, find_packages

version = '0.0.4'
name = 'audiblerangepy'
short_description = '`audiblerangepy` is a package for checking some frequency is audible or not for some human-being and animals'
long_description = """\
`audiblerangepy` is a package for checking some frequency is audible or not for some human-being and animals

Requirements
------------
* Python 3.x
(you may work by Python2.x)

Features
--------
* nothing

History
-------
0.0.1 (2017-7-15)
0.0.2 (2017-7-15)
0.0.3 (2017-7-15)
0.0.4 (2017-7-15)
~~~~~~~~~~~~~~~~~~
* first release

"""

setup(
    name=name,
    version=version,
    url='https://github.com/k-mawa/audiblerangepy',
    description=short_description,
    long_description=long_description,
    keywords=['audible','audible range'],
    packages=find_packages(),
    author='Kosuke Mawatari',
    license='MIT',
)