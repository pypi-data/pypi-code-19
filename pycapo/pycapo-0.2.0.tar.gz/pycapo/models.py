# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    import StringIO as stringio
except ImportError:
    import io as stringio

from pycapo import DEFAULT_CAPO_PATH

_ENV_PATTERN = re.compile('\$\{env:([a-zA-Z\_]+)\}')


class CapoConfig:
    r""" The class for fetching CAPO configuration settings.

    :Keyword Arguments:
        *profile* ("string"): the name of the profile to use, e.g. 'test', 'production'. If missing this defaults to the CAPO_PROFILE environment variable, if that is missing as well it explodes, throwing a ValueError exception. A profile should be a simple word, one without spaces or tabs or evil things in it. This is not checked and no guarantee is provided.

        *path* ("string"): a colon delimited path of capo directories to search, if missing defaults to the CAPO_PATH environment variable, if that is missing it defaults to pycapo.DEFAULT_CAPO_PATH.

    :Example:

    >>> from pycapo import *
    >>> c = CapoConfig(profile='test')
    >>> c.getstring('evla.casaHome')
    '/home/casa/packages/pipeline/current'
    >>> c['evla.casaHome']
    '/home/casa/packages/pipeline/current'
    >>> settings = c.settings('evla')
    >>> settings.casaHome
    '/home/casa/packages/pipeline/current'
    """

    def __init__(self, **kwargs):

        if 'profile' in kwargs and kwargs['profile']:
            self.profile = kwargs['profile']
        elif 'CAPO_PROFILE' in os.environ:
            self.profile = os.environ['CAPO_PROFILE']
        else:
            raise ValueError('could not determine profile')

        if 'path' in kwargs and kwargs['path']:
            self._path = kwargs['path']
        elif 'CAPO_PATH' in os.environ:
            self._path = os.environ['CAPO_PATH']
        else:
            self._path = DEFAULT_CAPO_PATH

        self._options, self._locations = dict(), dict()
        self._cfgfiles = [_CapoConfigurationFile(self.profile, d)
                          for d in self._path.split(':')]
        self._update()

    def _update(self):
        """ Update the options in the order the files are declared. """
        self._options.clear()
        for cfg in self._cfgfiles:
            d = cfg.getoptions()
            for key in d:
                self._options[key.upper()] = d[key]
                self._locations[key.upper()] = cfg.getfilename()

    def get(self, option):
        r""" Fetches a configuration option as a string.

        :Arguments:
            *option* ("string"): the name of the option to return, this shouldn't include whitespace of any kind.
        :return:
            the specified option as a string, and will throw a KeyError if the option is missing.
        """
        self._update()
        return self._options[option.upper()]

    def getint(self, option):
        r""" Fetches an configuration option as an int.

        :Arguments:
            *option* ("string"): the name of the option to return, this shouldn't include whitespace of any kind.
        :return:
            the specified option as an int, and will throw a KeyError if the option is missing, or a ValueError if the option can't be converted into an int.
        """
        return int(self.get(option))

    def getfloat(self, option):
        r""" Fetches a configuration option as a float.

        :Arguments:
            *option* ("string"): the name of the option to return, this shouldn't include whitespace of any kind.
        :return:
            the specified option as a float, and will throw a KeyError if the option is missing, or a ValueError if the option can't be converted into a float.
        """
        return float(self.get(option))

    def getboolean(self, option):
        r""" Fetches a configuration option as a boolean.

        :Arguments:
            *option* ("string"): the name of the option to return, this shouldn't include whitespace of any kind.
        :return:
            the specified option as a boolean, and will throw a KeyError if the option is missing, or a ValueError if the option can't be converted into a boolean.

        :Note:
           '1', 'on', 'yes', and 'true' are considered True
           '0', 'off', 'no', and 'false' are considered False
           The comparison ignores case, and this mapping of values might be nothing like what Java does, so be careful.
        """
        t = ['1', 'on', 'yes', 'true']
        f = ['0', 'off', 'no', 'false']
        val = self.get(option).lower()
        if val in t:
            return True
        elif val in f:
            return False
        raise ValueError('option {} not allowed'.format(val))

    def getstring(self, option):
        r""" Fetches a configuration option as a string.

        :Arguments:
            *option* ("string"): the name of the option, this shouldn't include whitespace of any kind.
        :return:
            the specified option as a string, and will throw a KeyError if the option is missing.
        """
        return self.get(option)

    def getoptions(self):
        r""" Returns all the options.

        :return:
            a dictionary mapping each option's name to its value as a string.
        """
        return dict(self._options)

    def getlocations(self):
        r""" Returns the locations of all the options.

        :return:
            a dictionary that maps each option's name to the properties file CapoConfig got it from.
        """
        return dict(self._locations)

    def has_option(self, option):
        r""" Check to see if we have a certain option.

        :Arguments:
            *option* ("string"): the name of the option, this shouldn't include whitespace of any kind.
        :return:
            True if we have a given option and False otherwise.
        """
        return option.upper() in self._options

    def get_location(self, option):
        r""" Find the location of a given option.

        :Arguments:
            *option* ("string"): the name of the option, this shouldn't include whitespace of any kind.
        :return:
            the path of the properties file we got a given option from (a string), and throws a KeyError if the option is missing.
        """
        return self._locations[option.upper()]

    def getpath(self):
        r""" The search path CapoConfig is using.

        :return:
            The search path (a string).
        """
        return self._path

    def __getitem__(self, option):
        r"""Return the string value of this option."""
        return self.getstring(option)

    def settings(self, prefix):
        r"""Return a Settings wrapper over this Capo instance with the supplied prefix.

        :Arguments:
            *prefix* ("string"): the prefix to use for searching Capo (e.g. OodtSettings or archive.deployment)
        :return:
            the settings wrapper for this prefix.
        """
        return Settings(self, prefix)


class _CapoConfigurationFile:
    def __init__(self, profile, directory):
        """
        Args:
            profile (string): the name of the profile to use, e.g. 'test',
            'production'. A profile should be a simple word, one without
            spaces or tabs or evil things in it. This is not checked and
            no guarantee is provided.

            directory (string): the directory the capo file lives in, the
            file should be $profile.properties, so if the directory is given
            as '/home/ssa/capo' and the profile is given as 'production', the
            capo file will be '/home/ssa/capo/production.properties'.
        """
        self._filename = os.path.join(directory, profile + '.properties')
        self._last_read = 0
        self._options = dict()
        self.getoptions()

    def _fix_env(self, s):
        """ Do environment variable expansion on a property value. """
        v = re.match(_ENV_PATTERN, s).group(1)
        return _ENV_PATTERN.sub(os.environ.get(v, ""), s)

    def getoptions(self):
        """
        Get properties from the file if it has changed since we did
        this last, otherwise return the results of the previous get.
        """
        if not os.path.exists(self._filename) or \
                not os.access(self._filename, os.R_OK):
            # If the file is missing or unreadable.
            self._options.clear()
            self._last_read = 0
        elif os.path.getmtime(self._filename) > self._last_read:
            # Else it is readable, is it newer than last time?
            cp = _SimpleConfigParser()
            cp.read(self._filename)
            self._options.clear()
            for opt in cp.getoptionslist():
                val = cp.getoption(opt)
                # Handle values that embed environment variables
                if re.match(_ENV_PATTERN, val):
                    self._options[opt] = self._fix_env(val)
                else:
                    self._options[opt] = cp.getoption(opt)
            self._last_read = os.path.getmtime(self._filename)
        return self._options

    def getfilename(self):
        return self._filename


class _SimpleConfigParser(configparser.RawConfigParser):
    """
    This extends the standard configparser in a way that allows it to deal
    with property files with no [sections] (like the kind Java expects), it
    does this by injecting a NOSECTION section at the top. I found it here:
    https://www.decalage.info/python/configparser.

    Note that as a consequence things will get messed up if somebody does
    put a real [section] in one of the config files.
    """
    NOSECTION = 'NOSECTION'

    def read(self, filename):
        text = open(filename, 'r').read()
        f = stringio.StringIO("[%s]\n" % self.NOSECTION + text)
        self.readfp(f, filename)

    def getoption(self, option):
        'get the value of an option'
        return self.get(self.NOSECTION, option)

    def getoptionslist(self):
        'get a list of available options'
        return self.options(self.NOSECTION)

    def hasoption(self, option):
        """
        return True if an option is available, False otherwise.
        (NOTE: do not confuse with the original has_option)
        """
        return self.has_option(self.NOSECTION, option)


class Settings:
    """Makes it easier to read Capo settings by grouping."""
    def __init__(self, capo, prefix):
        self._capo, self._prefix = capo, prefix

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, item):
        return self._capo.__getitem__(self._prefix + '.' + item)

    def __dir__(self):
        prefixlen = len(self._prefix) + 1
        return  [ key[prefixlen:].lower()
                  for key in self._capo.getoptions().keys()
                  if key.startswith(self._prefix.upper()) and
                  not '.' in key[prefixlen:] ]