#!/usr/bin/env python
from setuptools import setup, find_packages


def read(file_path):
    with open(file_path) as fp:
        return fp.read()


setup(
    name='desktopography',
    version='1.1',
    description="A simple desktopography.net wallpaper retriever",
    long_description=read('Readme.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Desktop Environment',
        'Topic :: Utilities',
    ],
    keywords=['desktopography', 'wallpapers'],
    author='Fabien Bochu',
    author_email='fabien.bochu+desktopography@gmail.com',
    url='https://gitlab.com/fbochu/desktopography',
    license='BSD',
    packages=find_packages(where='src'),
    package_dir={'': str('src')},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'BeautifulSoup4',
        'requests',
    ],
    entry_points={
        'console_scripts': (
            'desktopography = desktopography.cli:main',
        ),
    },
)
