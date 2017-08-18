import os, sys
try:
    from setuptools import setup, find_packages
    use_setuptools = True
except ImportError:
    from distutils.core import setup
    use_setuptools = False

try:
    with open('README.md', 'rt') as readme:
        description = '\n' + readme.read()
except IOError:
    # maybe running setup.py from some other dir
    description = ''

install_requires = [
    'tatsu>=4.1.1',
    'jinja2>=2.9.6'
]

setup(
    name="rxtender",
    version='0.1.1',
    url='https://github.com/rxtender/rxtender',
    license='MIT',
    description="Reactive streams IPC and RPC code generator",
    long_description=description,
    author='Romain Picard',
    author_email='romain.picard@oakbits.com',
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Debuggers'
    ],
    scripts=['script/rxtender'],
)
