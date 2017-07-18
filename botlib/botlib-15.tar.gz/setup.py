#!/usr/bin/env python3

""" botlib setup.py """

import os
import sys

if sys.version_info.major < 3:
    print("you need to run BOTLIB with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

setup(
    name='botlib',
    version='15',
    url='https://bitbucket.org/bthate/botlib',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Framework to program bots",
    license='Public Domain',
    include_package_data=False,
    zip_safe=False,
    install_requires=["sleekxmpp", "feedparser", "dnspython", "pyasn1", "pyasn1_modules"],
    scripts=["bin/bot", "bin/bot-udp"],
    packages=['botlib'],
    extra_path="botlib",
    long_description='''BOTLIB - Framework to program bots

provides:

* CLI, IRC and XMPP bots.
* Object class  - save/load to/from a JSON file.
* ReST server - serve saved object's over HTTP.
* RSS fetcher - echo rss feeds to IRC channels.
* UDP server -  udp to bot to IRC channel.
* Watcher server - run tail -f and have output send to IRC channel.
* Email scanning - scan mbox format to searchable BOTLIB objects.
* JSON backend - objects are stored as json string in files on the fs.
* Db - iteration over stored objects.
* timebased filenames gives logging capabilities
* future sensors should provide entry to the logger.

setup:

* Set export PYTHONPATH="." if the bot cannot be found by the python interpreter.
* Set export PYTHONIOENCODING="utf-8" if your shell has problems with handling utf-8 strings.
* For the XMPP server use a ~/.sleekpass file with the password in it

contact:

* Bart Thate
* botfather on #dunkbot irc.freenode.net
* bthate@dds.nl, thatebart@gmail.com

BOTLIB is code released in the Public Domain - https://bitbucket.org/bthate/botlib


''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Public Domain',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
