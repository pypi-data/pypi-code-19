#!/usr/bin/env python3
#
#

import os
import sys

if sys.version_info.major < 3:
    print("you need to run madbot with python3")
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
    version='10',
    url='https://bitbucket.org/bthate/botlib',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Framework to program bots. JSON backend, MIT license.",
    license='MIT',
    include_package_data=False,
    zip_safe=False,
    install_requires=["sleekxmpp", "feedparser", "dnspython", "pyasn1", "pyasn1_modules"],
    scripts=["bot", "bot-udp", "bot-local", "bot-do"],
    packages=['botlib'],
    long_description='''
    
BOTLIB is a python3 framework to program IRC or XMPP bots.

provides:

| CLI, IRC and XMPP bots.

| MIT license, allowed derived copying.
| modular structure, easy to program.

| object class  - save/load to/from a JSON file.
| rest server - serve saved object's over HTTP.
| rss fetcher - echo rss feeds to IRC channels.
| udp server -  udp to bot to IRC channel.
| watcher server - run tail -f and have output send to IRC channel.
| email scanning - scan mbox format to searchable BOTLIB objects.

email:

| Bart Thate
| botfather on #dunkbots irc.freenode.net
| bthate@dds.nl, thatebart@gmail.com
|
|
| BOTLIB is code released onder een MIT compatible license.


''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
