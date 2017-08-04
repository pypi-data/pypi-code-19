import re
from setuptools import setup, find_packages


with open('testdocker/__init__.py', 'rt') as fd:
    data = fd.read()
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        data, re.MULTILINE).group(1)
    name = re.search(r'^__title__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        data, re.MULTILINE).group(1)
    del data

for prop in ('version', 'name'):
    if not globals().get(prop):
        raise RuntimeError('Cannot find %s information' % prop)

with open('README.rst') as fd:
    long_description = fd.read()


setup(
    name=name,
    version=version,
    description='Testing for docker containers',
    long_description=long_description,
    keywords=['docker', 'docker-compose', 'testing'],
    author='Joe Black',
    author_email='joeblack949@gmail.com',
    url='https://github.com/joeblackwaslike/%s' % name,
    download_url=(
        'https://github.com/joeblackwaslike/%s/tarball/%s' % (name, version)),
    license='Apache 2.0',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    install_requires=[
        'requests',
        'PyYAML',
        'docker',
        'colour_runner',
    ],
    entry_points=dict(
        console_scripts=['testdocker=testdocker.cli.main:main']
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3 :: Only',
    ]
)
