from setuptools import setup

setup(
    name='armada-heal',
    description='Script for healing overloaded armada ship.',
    version='0.0.3',
    url='http://dev.git.gd/armada/armada-heal',
    author='Cerebro',
    author_email='cerebro@ganymede.eu',
    packages=['armada_heal'],
    scripts=['armada_heal/armada-heal'],
    install_requires=['requests'],
)
