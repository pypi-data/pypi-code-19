#!/usr/bin/env python3

from setuptools import setup

VERSION = '0.1.7'

setup(name='jabbergram',
      version=VERSION,
      description='XMPP/Jabber - Telegram Gateway.',
      long_description=open('README.rst', encoding='utf-8').read(),
      author='drymer',
      author_email='drymer@autistici.org',
      url='http://git.daemons.it/drymer/jabbergram/about/',
      download_url='https://git.daemons.it/drymer/jabbergram/archive/' + VERSION + '.tar.gz',
      scripts=['jabbergram.py'],
      license="GPLv3",
      install_requires=[
          "sleekxmpp>=1.3.2",
          "python-telegram-bot>=6.1.0",
          "requests>=2.11.1",
          ],
      classifiers=["Development Status :: 4 - Beta",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Operating System :: OS Independent",
                   "Operating System :: POSIX",
                   "Intended Audience :: End Users/Desktop"]
      )
