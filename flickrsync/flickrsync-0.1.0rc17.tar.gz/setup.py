from setuptools import setup, find_packages

setup(
    name='flickrsync',
    version='0.1.0rc17',
    description='A command line tool to synchronise pictures between the local file system and Flickr',
    url='https://github.com/danchal/flickrsync',
    author='Dan Chal',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests*']),
    license='GPL3',
    install_requires=[
        'flickrapi>=2.2.1',
        'Wand>=0.4.4',
        'configparser',
    ],
    scripts=['bin/flickrsync'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='flickr upload backup photo sync',
    zip_safe=False,
    include_package_data=True,
    package_data={'flickrsync': ['etc/config.ini']}
)
