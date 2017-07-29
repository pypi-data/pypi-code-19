import glob
from distutils.core import setup

from pip.req import parse_requirements
from setuptools import find_packages

requirements = [str(ir.req) for ir in parse_requirements('requirements.txt', session='hack')]

with open('VERSION') as version_file:
    version = version_file.readlines()[0].strip()

data_files_extensions = ['html', 'ini', 'tplt', 'css', 'js']
data_files = []
prefix_len = len('djotali/')
for extension in data_files_extensions:
    data_files += [data_file[prefix_len:] for data_file in glob.iglob('djotali/**/*.' + extension, recursive=True)]

setup(
    name='djotali',
    version=version,
    packages=find_packages(exclude=('venv', 'tests',)),
    url='',
    license='MIT',
    author='Pascal Ekouaghe',
    author_email='ekougs@gmail.com',
    description='Our SAAS solution to easily send messages to your clients',
    install_requires=requirements,
    package_data={
        'djotali': data_files
    },
    scripts=['scripts/launch_djotali', 'manage.py'],
)
