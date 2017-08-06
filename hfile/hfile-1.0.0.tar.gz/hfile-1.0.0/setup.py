
from setuptools import setup


setup(
    name='hfile',
    version='1.0.0',
    license='MIT',
    py_modules = ['hfile'],
    install_requires=['click', 'colorama'],
    entry_points={
        'console_scripts': [
            'hfile=hfile.cli:main',
        ],
    },
)