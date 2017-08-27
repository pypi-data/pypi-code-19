#!/usr/bin/env python
"""PyPi Configuration File Manager."""

import optparse
import os

try:
    import configparser
    from urllib.parse import urlparse, urlunparse

except ImportError:
    import ConfigParser as configparser
    from urlparse import urlparse, urlunparse


class SetPyPi(object):
    """
    PyPi Configuration File Manager.

    Can be used for updating ~/.pypirc file programatically.

    Example::
        >>> a = SetPyPi('doctest_pypi.cfg')
        >>> new_server = {'pypi': {'repository': 'http://pypi.example.com'}}
        >>> new_server2 = {'pypi2': {'repository': 'http://pypi2.example.com'}}
        >>> a.servers.update(new_server)
        >>> a.servers.update(new_server2)
        >>> a.save()
        >>> 'pypi' in a.servers
        True
        >>> 'pypi2' in a.servers
        True
    """

    RC_FILE = os.path.join(os.path.expanduser('~'), '.pypirc')

    def __init__(self, rc_file=None, pip_conf=None):
        if rc_file is None:
            self.rc_file = self.RC_FILE
        else:
            self.rc_file = rc_file

        if pip_conf is None:
            self.pip_conf = self._get_pip_conf()
        else:
            self.pip_conf = pip_conf

        self.conf = configparser.ConfigParser()

        if os.path.exists(self.rc_file):
            self.conf.read(self.rc_file)

        self._create_distutils()

        self._servers = {}
        for server in self._get_index_servers():
            if self.conf.has_section(server):
                server_conf = {server: dict(self.conf.items(server))}
                self.servers.update(server_conf)

    def _create_distutils(self):
        """Creates top-level distutils stanza in pypirc."""
        if not self.conf.has_section('distutils'):
            self.conf.add_section('distutils')

    def save(self):
        return self.save_pypirc()

    def save_pypirc(self):
        """Saves pypirc file with new configuration information."""
        for server, conf in self.servers.items():
            self._add_index_server()
            for conf_k, conf_v in conf.items():
                if not self.conf.has_section(server):
                    self.conf.add_section(server)
                self.conf.set(server, conf_k, conf_v)

        with open(self.rc_file, 'w') as configfile:
            self.conf.write(configfile)
            print('.pypirc configured. %s' % self.rc_file)
        self.conf.read(self.rc_file)

    def _get_index_servers(self):
        """Gets index-servers current configured in pypirc."""
        idx_srvs = []
        if 'index-servers' in self.conf.options('distutils'):
            idx = self.conf.get('distutils', 'index-servers')
            idx_srvs = [srv.strip() for srv in idx.split('\n') if srv.strip()]
        return idx_srvs

    def _add_index_server(self):
        """Adds index-server to 'distutil's 'index-servers' param."""
        index_servers = '\n\t'.join(self.servers.keys())
        self.conf.set('distutils', 'index-servers', index_servers)

    @property
    def servers(self):
        """index-servers configured in pypirc."""
        return self._servers

    @servers.setter
    def servers(self, server):
        """Adds index-servers to pypirc."""
        self._servers.update(server)

    def save_pipconf(self, server_alias='pypi', just_trust=False):
        server = self.servers.get(server_alias)
        if server is None:
            print('cannot find server_alias %s' % server_alias)
            return False

        repository = server['repository']
        repository_domain = urlparse(repository).netloc

        if server.get('username') and server.get('password'):
            o = list(urlparse(repository))
            o[1] = '%s:%s@%s' % (server['username'], server['password'], o[1])
            repository = urlunparse(o)

        cfg = configparser.ConfigParser()
        cfg.read(self.pip_conf)
        G = 'global'

        if not cfg.has_section(G):
            cfg.add_section(G)

        get_or_empty = lambda option: cfg.get(G, option) if cfg.has_option(G, option) else ''  # @IgnorePep8
        set_clean = lambda option, value: cfg.set(G, option, value.strip())  # @IgnorePep8

        if not just_trust:
            pre_index_url = get_or_empty('index-url')
            if pre_index_url is not repository:
                set_clean('index-url', repository)

        pre_trusted_hosts = get_or_empty('trusted-host')
        if repository_domain not in pre_trusted_hosts:
            set_clean('trusted-host', repository_domain + '\n' + pre_trusted_hosts)

        set_clean('extra-index-url', 'https://pypi.python.org/simple')
        # if cfg.has_option(G, 'extra-index-url'):
        #     cfg.remove_option(G, 'extra-index-url')

        try:
            os.makedirs(os.path.dirname(self.pip_conf))
        except OSError:
            pass

        with open(self.pip_conf, 'w') as fp:
            cfg.write(fp)
            print('%s configured. %s' % (os.path.basename(self.pip_conf), self.pip_conf))

    def _get_pip_conf(self):
        virtual_env = os.environ.get('VIRTUAL_ENV')
        if virtual_env is None:
            if os.name == 'nt':
                path_to = os.path.join(os.path.expanduser('~'), 'pip')
            else:
                path_to = os.path.join(os.path.expanduser('~'), '.config/pip')
        else:
            path_to = os.path.abspath(virtual_env)

        if os.name == 'nt':
            pip_conf = os.path.join(path_to, 'pip.ini')
        else:
            pip_conf = os.path.join(path_to, 'pip.conf')
        return pip_conf

    def handle_args(self, args=None, **defaults):
        parser = optparse.OptionParser()
        parser.add_option(
            '-s', '--server', help='Index Server Name [default: pypi]', metavar='SERVER', default='pypi')
        parser.add_option(
            '-r', '--repository', help='Repository URL', metavar='URL')
        parser.add_option(
            '-u', '--username', help='User Name', metavar='USERNAME')
        parser.add_option(
            '-p', '--password', help='Password', metavar='PASSWORD')
        parser.add_option(
            '', '--no-pypirc', help='do not write ~/.pypirc', dest='write_pypirc', default=True, action='store_false')
        parser.add_option(
            '', '--no-pipconf', help='do not write pip.conf', dest='write_pipconf', default=True, action='store_false')
        parser.add_option(
            '', '--just-trust', help='just write trust to pip.conf', dest='just_trust', default=False,
            action='store_true')

        if defaults:
            parser.set_defaults(**defaults)
        options, args = parser.parse_args(args)

        if args:
            if len(args) == 1 and options.repository is None:
                options.repository = args[0]
            else:
                raise ValueError('cannot process args ')

        self.set(options.repository, options.username, options.password,
                 options.server, options.write_pypirc, options.write_pipconf, options.just_trust)

    def set(self, repository, username=None, password=None, server_alias='pypi',
            write_pypirc=False, write_pipconf=False, just_trust=False):
        if repository and '@' in repository:
            if (username or password):
                raise ValueError('plese set one user-pass')
            else:
                o = urlparse(repository)
                username = o.username
                password = o.password
                netloc = o.hostname
                if o.port:
                    netloc += ":%s" % o.port
                o = list(o)
                o[1] = netloc
                repository = urlunparse(o)

        if server_alias:
            server = self.servers.get(server_alias, {})
            server['repository'] = repository or ''
            server['username'] = username or ''
            server['password'] = password or ''

            self.servers[server_alias] = server

            if write_pypirc:
                self.save_pypirc()

            if write_pipconf:
                self.save_pipconf(server_alias, just_trust)

        else:
            print('.pypirc Empty!')


def handle_args():
    SetPyPi().handle_args()


def handle_args_only_pipconf():
    SetPyPi().handle_args(write_pypirc=False)


def handle_args_only_pypirc():
    SetPyPi().handle_args(write_pipconf=False)


def trust_host():
    SetPyPi().handle_args(write_pypirc=False, just_trust=True)


if __name__ == '__main__':  # pragma: no cover
    handle_args()
