from setuptools import setup

def load_dependencies():
    with open('requirements.txt') as dependencies:
            return dependencies.read().splitlines()

setup(
    name='animus-omni',
    version = '0.0.1',
    license = 'MIT',
    author = 'Animus Intelligence, LLC',
    author_email = 'info@animus.io',
    description = 'Animus commandline tools to reduce Internet radiation from log files',
    packages = ['animus', 'animus.LogParsers'],
    scripts = ['omni-reduce'],
    py_modules = ['animus'],
    install_requires = load_dependencies(),
    url = 'https://github.com/Animus-Intelligence/omni',
    classifiers = ['Development Status :: 3 - Alpha'],
    )
