import os
from setuptools import setup, find_packages

requirements = [l.split('=')[0] for l in open('requirements.txt', 'r').read().split('\n') if l]

def read(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

'''
python setup.py register -r pypi # run this only once to setup your environment
python setup.py sdist upload -r pypi
'''

setup(
    name='highlyprobable',
    version='0.0.1.7',
    description=(
        'Client for HighlyProbable Cloud AI Framework.'
    ),
    url='https://github.com/Tranquant/HighlyProbable/',
    author='Mehrdad Pazooki',
    author_email='mehrdad@tranquant.com',
    license='Apache 2.0',
    install_requires=requirements,
    py_modules=[
        'highlyprobable.highlyprobable',
        'highlyprobable.base',
        'highlyprobable.config',
        'highlyprobable.api',
    ],
    keywords = [
        'Data Science', 'AI', 'Machine Learning', 'Natural Language Processing',
        'Recommendation', 'Apache Spark', 'Classification'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
    ],
    platforms='any',
    zip_safe=True
)