# https://packaging.python.org/tutorials/distributing-packages/

from setuptools import setup
import os


setup(
    name='no_you_talk_to_the_hand',
    version='0.3',
    author='flashashen',
    description='Boss your corporate network effortlessly. Automatic and organized tunneling with sshuttle + supervisord + yaml',
    license = "MIT",
    keywords = "ssh vpn tunnel forward daemonn",
    # long_description=read('README.md'),
    py_modules=['no_you_talk_to_the_hand'],
    install_requires=[
        'Click',
        'supervisor',
        'pyyaml',
        'jinja2'
    ],

    entry_points='''
        [console_scripts]
        yth=no_you_talk_to_the_hand:cli
    ''',
)