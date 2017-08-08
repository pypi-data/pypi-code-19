from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='patella',
    packages=find_packages(),
    version='0.1.10',
    author='Salvador Brandi',
    author_email='salbrandi@gmail.com',
    url='https://github.com/salbrandi/patella',
    download_url='https://github.com/salbrandi/patella/archive/0.1.tar.gz',
    py_modules=['htmlparser'],
    description='A webservice for scraping files and plotting data against presidential party variation',
    long_description=long_description,
    entry_points='''
        [console_scripts]
        patella=patella.click_commands:patella
        ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='plotting data party presidential office term year bokeh'
)
