from setuptools import setup

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(
    name='Tokage',
    author='SynderBlack',
    version='0.1.6.4',
    packages=['tokage'],
    license='MIT',
    description='Async wrapper for the MyAnimeList API',
    include_package_data=True,
    install_requires=requirements
)
