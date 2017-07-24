from distutils.core import setup

setup(
    name='slackchannelreader',
    packages=['slackchannelreader'],
    install_requires=[
        "slackclient",
        "httplib2",
    ],
    version='0.0.1',
    description='simple slack client which polls messages and images from a given channel.',
    author='Thomas Irgang',
    author_email='thomas@irgang-la.de',
    url='https://github.com/irgangla/slackchannelreader',
    download_url='https://github.com/irgangla/slackchannelreader',
    keywords=['Slack', 'client', 'channel', 'chat', 'download'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description="""\
SlackChannelReader
------------------

This is a very simple Slack client (using legacy auth) which is able to poll
* messages
* images
from a given Slack channel.

It is intended as data source for info displays.

This version requires Python 3 or later.
"""
)
