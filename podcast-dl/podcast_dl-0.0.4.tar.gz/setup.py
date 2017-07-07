#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import podcast_dl

setup(
  name='podcast_dl',
  version='0.0.4',
  packages=find_packages(),
  author='Jorrin Pollard',
  author_email='me@jorrinpollard.com',
  description='Command-line program for downloading podcasts',
  url='https://github.com/podcast-dl/podcast-dl',
  long_description='README at https://github.com/podcast-dl/podcast-dl',
  license='MIT',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Topic :: Multimedia :: Sound/Audio',
  ],
  keywords=[
    'podcast',
    'podcasts',
    'podcasting',
    'download',
    'downloads',
    'downloading',
    'scrape',
    'scraper',
    'scrapers',
    'scraping',
    'tag',
    'tags',
    'tagger',
    'taggers',
    'tagging',
    'audio',
    'mp3',
  ],
  install_requires=[
    'appdirs',
    'bs4',
    'click',
    'clint',
    'colorama',
    'feedparser',
    'mutagen',
    'peewee',
    'Pillow',
    'python-dateutil',
    'requests',
    'unicode-slugify',
    'pprint'
  ],
  entry_points={
    'console_scripts': [
      'podcast-dl = podcast_dl.cli:main',
    ],
  },
)