from setuptools import setup
import sys

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name='workaround',
    version='0.1.1',
    packages=['workaround', 'workaround.handlers'],
    url='',
    license='',
    author='Tom Forbes',
    author_email='tom@tomforb.es',
    description='',
    install_requires=[
        'requests',
        'docopt',
        'colorama',
        'termcolor',
        'requests',
        'packaging',
        'semver',
        'regex',
        'typing; python_version < "3.6"',
    ],
    setup_requires=pytest_runner,
    entry_points={
        'console_scripts': [
            'workaround = workaround.cli:run'
        ],
        'workaround_handlers': [
            'github = workaround.handlers.github:GithubHandler',
            'pypi = workaround.handlers.pypi:PyPiHandler',
            'django = workaround.handlers.django:DjangoHandler',
            'npm = workaround.handlers.npm:NPMHandler'
        ]
    }
)
