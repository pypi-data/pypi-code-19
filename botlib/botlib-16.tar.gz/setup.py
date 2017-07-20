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
    version='16',
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
    long_description='''
README
######

BOTLIB is a python3 framework to use if you want to program IRC or XMPP bots.

provides:

| CLI, IRC and XMPP bots.

| Object class 		- save/load to/from a JSON file.
| ReST server 		- serve saved object’s over HTTP.
| RSS fetcher 		- echo rss feeds to IRC channels.
| UDP server 		- udp to bot to IRC channel.
| Watcher server 	- run tail -f and have output send to IRC channel.
| Email scanning 	- scan mbox format to searchable BOTLIB objects.
| JSON backend 		- objects are stored as json string in files on the fs.
| Db	 		- iteration over stored objects.
| Timestamp		- time based filenames gives logging capabilities
| Future		- future sensors should provide entry to the logger.

setup:

| Set export PYTHONPATH=”.” if the bot cannot be found by the python interpreter.
| Set export PYTHONIOENCODING=”utf-8” if your shell has problems with handling utf-8 strings.
| For the XMPP server use a ~/.sleekpass file with the password in it

source:

| botlib		- botlib package.
| botlib.bot		- bot base class.
| botlib.cli 		- command line interfacce bot, gives a shell prompt to issue bot commands.
| botlib.clock 		- timer, repeater and other clock based classes.
| botlib.cmnds 		- botlib basic commands.
| botlib.compose 	- construct a object into it’s type.
| botlib.engine 	- select.epoll event loop, easily interrup_table esp. versus a blocking event loop.
| botlib.db 		- JSON file db.
| botlib.error 		- botlib exceptions.
| botlib.event 		- event handling classes.
| botlib.fleet 		- fleet is a list of bots.
| botlib.handler 	- schedule events.
| botlib.irc 		- IRC bot class.
| botlib.kernel 	- program boot and module loading.
| botlib.launcher 	- a launcher launches threads (or tasks in this case).
| botlib.log 		- log module to set standard format of logging.
| botlib.object 	- JSON file backed object with dotted access.
| botlib.raw 		- raw output using print.
| botlib.rss 		- rss module.
| botlib.selector 	- functions used in code to select what objects to use.
| botlib.task 		- adapted thread to add extra functionality to threads.
| botlib.trace 		- functions concering stack trace.
| botlib.users 		- class to access user records.
| botlib.xmpp 		- XMPP bot class.
| botlib.register 	- object with list for multiple values.
| botlib.rest 		- rest interface.
| botlib.runner 	- threaded loop to run tasks on.
| botlib.space 		- central module to store objects in.
| botlib.static 	- static definitions.
| botlib.template 	- cfg objects containing default values for various services and plugins.
| botlib.test 		- plugin containing test commands and classes.
| botlib.udp 		- relay txt through a udp port listener.
| botlib.utils 		- lib local helper functions.
| botlib.url 		- functions that fetch data from url.
| botlib.watcher 	- watch files.

contact:

| Bart Thate
| botfather on #dunkbot irc.freenode.net
| bthate@dds.nl, thatebart@gmail.com

BOTLIB is code released in the Public Domain - https://bitbucket.org/bthate/botlib


''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Public Domain',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
