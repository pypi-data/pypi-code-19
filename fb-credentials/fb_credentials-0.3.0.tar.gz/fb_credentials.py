"""
==============================================
Extend login Interface for fogbugz
Parts of this code comes from the fborm project
==============================================
"""

from __future__ import print_function
import getpass
import contextlib
import os
import re

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

__version__ = (0,3,0)
__version_string__ = '.'.join(str(x) for x in __version__)

__author__ = 'Nicolas Morales'
__email__ = 'portu.github@gmail.com'

CREDENTIALTYPES = ('token', 'username', 'password')
def get_input(prompt):
    '''Wrapper around builtin function raw_input in order to mock it in tests'''
    return raw_input(prompt)

def get_credential(credentialtype, fogbugzrc=None, fogbugzprefix='', interactive=True):
    """ get credential from fogbugzrc or prompt user
        credentialtype: One in CREDENTIALTYPES
        fogbugzrc: Path to configuration file
        fogbugzprefix: prefix for credential. Useful if the fogbugzrc is used for multiple servers
                 with different credentials
        interactive: If credentials not found in fogbugzrc and this option is set, prompt the user
    """
    if credentialtype not in CREDENTIALTYPES:
        raise ValueError('option credential can only take values {}. Passed: {}'.format(CREDENTIALTYPES, credentialtype))
    #Search whether there is a fogbugzrc file
    if not fogbugzrc:
        fogbugzrc = os.path.join(os.path.expanduser("~"), '.fogbugzrc')

    credential = None
    if os.path.isfile(fogbugzrc):
        for line in open(fogbugzrc):
            line = line.split('#')[0]
            if fogbugzprefix + credentialtype in line:
                res = re.search(r'{}\s*=\s*(\S+)'.format(credentialtype), line)
                credential = res.group(1)
    if not credential and interactive:
        if credentialtype is 'password':
            credential = getpass.getpass('password: ')# Same as raw_input but hide what user types
        else:
            credential = get_input(credentialtype + ': ')
    return credential

def validate_token(hostname, token):
    """ Validate the user token.

        Returns True for a successful validation, False otherwise
    """
    if token:
        url = hostname + "/api.asp?cmd=logon&token=" + token
        try:
            response = urlopen(url)
            if token in response.read():
                return True
        except:
            pass # Always catch authentication error and return (other methods may be attempted)
        print('Failed to use token provided')
    return False

def FogBugz(fbConstructor, hostname, token=None, username=None, password=None, fogbugzrc=None,
            fogbugzPrefix='', interactive=True, storeCredentials=False):
    """ Calls the constructor specified by fbConstructor (hence, despite this being a function use
        CapWords naming convention)

        fbConstructor: Fogbugz constructor class. Typically fogbugz.FogBugz, fborm.FogBugzORM or
                       kiln.Kiln
        hostname: passed directly to the fbInterface
        token, username, password: input credentials
        fogbugzrc, fogbugzPrefix, interactive: Passed to method get_credential
        storeCredentials: If active, create attributes token, username and password. This opens the
                          door to using it for login to other system, which is convenient, but the
                          programmer can also do what he wants with the password (which is bad).

        The following is attempted in sequence:
            1. Use token provided
            2. Use username provided
            3. Get token with function get_credential
            4. Get username and password with function get_credential (interactive=True)

        TODO: Support passing a list of args to fbConstructor
    """
    if token and (username or password):
        raise TypeError("If you supply 'token' you cannot supply 'username' or 'password'")

    if token and validate_token(hostname, token):
        fb = connect(fbConstructor, hostname, token=token)
    elif username:
        if not password:
            password = get_credential('password', fogbugzrc, fogbugzPrefix, interactive)
        fb = connect(fbConstructor, hostname, username=username, password=password)
    else:
        token = get_credential('token', fogbugzrc, fogbugzPrefix, interactive=False)
        if validate_token(hostname, token):
            fb = connect(fbConstructor, hostname, token=token)
        else:
            username = get_credential('username', fogbugzrc, fogbugzPrefix, interactive)
            password = get_credential('password', fogbugzrc, fogbugzPrefix, interactive)
            fb = connect(fbConstructor, hostname, username=username, password=password)

    if storeCredentials:
        fb.token = token
        fb.username = username
        fb.password = password

    return fb

def connect(fb_constructor, hostname, token=None, username=None, password=None):
    ''' Call constructor fb_constructor and log on'''
    if bool(token) == bool(username):
        raise TypeError("If you pass 'token' you cannot supply 'username'")

    if bool(username) != bool(password):
        raise TypeError("username and password should be set both or none")

    if token:
        fb = fb_constructor(hostname, token=token)
    else:
        fb = fb_constructor(hostname)
        fb.logon(username, password)

    return fb

@contextlib.contextmanager
def FogBugz_cm(fbConstructor, hostname, logoff=False, **kwargs):
    ''' Context manager with logOff functionality'''
    fb = FogBugz(fbConstructor, hostname, **kwargs)
    yield fb

    if logoff:
        fb.logoff()
