# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<aljosha.friemann@gmail.com> wrote this file.  As long as you retain this
notice you can do whatever you want with this stuff. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

"""

import re, logging, os, shutil, requests

logger = logging.getLogger(__name__)

logging.getLogger('requests').setLevel(logging.WARNING)

class UndefinedSourceException(RuntimeError):
    def __str__(self):
        return "Found undefined source: {}".format(', '.join(self.args))

class UnsupportedSourceException(RuntimeError):
    def __str__(self):
        return "Source not yet supported: {}".format(', '.join(self.args))

class NoSuchFileException(RuntimeError):
    def __str__(self):
        return "No such file: {}".format(', '.join(self.args))

class AuthenticationException(RuntimeError):
    pass

class github:
    pattern = re.compile(r'^(http(s)?://)?(www\.)?github.com/.*')

    @staticmethod
    def build_url(url, branch, path):
        repo = url.split('github.com/')[-1]
        return '/'.join([ 'https://raw.githubusercontent.com', repo, branch or 'master', path ])

    @staticmethod
    def match(path):
        return github.pattern.match(path) is not None

    @staticmethod
    def get(source, path, target):
        url  = github.build_url(source.url, source.branch, path)
        auth = (source.user, source.password) if (source.user and source.password) else None

        logger.debug('retrieving from github raw file url: %s', url)
        response = requests.get(url, auth=auth)

        if response.status_code == 404:
            raise NoSuchFileException(url)

        with open(target, 'wb') as stream:
            stream.write(response.text.encode())

def get(path, source, target):
    if source is not None:
        logger.debug('retrieving %s to %s', source, target)

        if github.match(source.url):
            github.get(source, path, target)
        else:
            raise UnsupportedSourceException(source)
    else:
        shutil.copy(os.path.expanduser(path), target)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
