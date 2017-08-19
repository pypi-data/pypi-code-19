from setuptools import setup

setup(
    name='bookmark-config',
    description='Python module for fetching configuration values for Bookmark services.',
    author='Bookmark Novels',
    version='1.1.0',
    packages=['bookmark_config'],
    url='https://github.com/Bookmark-Novels/Bookmark-Config',
    license='MIT',
    install_requires=[
        'python-consul==0.7.1'
    ]
)
