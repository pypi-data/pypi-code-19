import os
from setuptools import setup, find_packages


if os.path.exists('README.rst'):
    long_description = open('README.rst', 'r').read()
else:
    long_description = 'See https://bitbucket.org/netlandish/sendypy/'


setup(
    name='sendypy',
    version=__import__('sendy').get_version(),
    packages=find_packages(),
    description='Python Interface for the Sendy API',
    author='Netlandish Inc.',
    author_email='hello@netlandish.com',
    url='https://bitbucket.org/netlandish/sendypy/',
    long_description=long_description,
    platforms=['any'],
    install_requires=['requests>=2.6.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Environment :: Web Environment',
    ],
    include_package_data=True,
)
