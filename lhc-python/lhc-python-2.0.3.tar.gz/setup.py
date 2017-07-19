import os

from subprocess import Popen, PIPE
from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') if os.path.exists('README.rst') else \
        open('README.md', encoding='utf-8') as fileobj:
    long_description = fileobj.read()

if os.path.exists('.git'):
    prc = Popen(['git', 'describe', '--tags', '--dirty'],
                stdout=PIPE,
                cwd=os.path.dirname(os.path.realpath(__file__)))
    version, _ = prc.communicate()
    version = version.decode(encoding='utf-8').strip()
else:
    version = os.path.basename(os.path.dirname(os.path.realpath(__file__))).rsplit('-', 1)[1]

setup(
    name='lhc-python',
    version=version,
    author='Liam H. Childs',
    author_email='liam.h.childs@gmail.com',
    packages=find_packages(exclude=['docs', 'test*']),
    scripts=[],
    url='https://github.com/childsish/lhc-python',
    license='LICENSE.txt',
    description='My python library of classes and functions that help me work',
    long_description=long_description,
    install_requires=['sortedcontainers == 1.5.3'],
    extras_require={ 'indexing': ['pysam'] },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics']
)
