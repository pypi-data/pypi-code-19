import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='qg_utils',
    version='0.0.3',
    description='',
    url='https://github.com/quantumgraph/qg_utils',
    author='QuantumGraph',
    author_email='contact@quantumgraph.com',
    license='MIT',
    packages=find_packages(),
    long_description=read('README.txt'),
    zip_safe=False,
    include_package_data=True,
    classifiers=[],
)
