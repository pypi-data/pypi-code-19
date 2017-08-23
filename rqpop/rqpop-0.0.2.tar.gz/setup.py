from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rqpop',
    packages=find_packages(),
    version='0.0.2',
    author='Salvador Brandi',
    author_email='salbrandi@gmail.com',
    url='https://github.com/salbrandi/rqpop',
    download_url='https://github.com/salbrandi/rqpop/archive/0.1.tar.gz',
    py_modules=['cpustresser'],
    description='A package to enqueue a variable number of jobs with variably distributed TIME x CPU "areas"',
    long_description=long_description,
    install_requires=[
                     'click',
                     'stressypy',
                     'scipy',
                     'rq',
                     'redis'
                     ],
    entry_points='''
        [console_scripts]
        rqpop=rqpop.cli:rqpop
        ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='rq queue distribution scipy tetris-queue tetris test loads populate population job enqueue backfill'
)
