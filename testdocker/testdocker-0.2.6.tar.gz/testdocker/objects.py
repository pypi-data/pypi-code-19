"""
testdocker.objects
~~~~~~~~~~~~~~~~~~

Classes for interacting with docker-compose and docker.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import time

import docker
from requests.exceptions import HTTPError
import yaml

from . import util


class Compose:
    """A Class for interacting with the `docker-compose` cli command."""

    DEFAULT_FILES = ('docker-compose.yml', 'docker-compose.yaml')
    defaults = dict(
        globals=dict(
            options=dict(
                files=DEFAULT_FILES
            ),
            flags=[],
        ),
        up=['daemonize', 'no_build'],
        down=['volumes']
    )

    def __init__(self, options=None, flags=None):
        self.options = util.set_defaults(
            options or {}, self.defaults['globals']['options'])
        self.flags = util.set_defaults(
            flags or [], self.defaults['globals']['flags'])
        self._discover_compose_files()

    def _discover_compose_files(self):
        self.options['files'] = [file for file in
                                 util.filter_dupes(self.options['files'])
                                 if os.path.exists(file)]

    def _build_global_args(self):
        args = []
        for key in self.options:
            if key == 'files':
                files = self.options[key]
                args.extend(['--file {}'.format(file) for file in files])
            elif key == 'project_name':
                args.append('--project-name {}'.format(self.options[key]))
        for flag in self.flags:
            args.append(util.format_flag(flag))
        return args

    def _build_command_args(self, command, flags=None):
        flags = util.set_defaults(flags or [], self.defaults[command])
        args = []
        if command == 'up':
            for flag in flags:
                if flag == 'daemonize':
                    args.append('-d')
                else:
                    args.append(util.format_flag(flag))
        elif command == 'down':
            for flag in flags:
                args.append(util.format_flag(flag))
        return list(util.filter_dupes(args))

    def _build_args_for(self, command, flags=None):
        flags = flags or []
        args = {}
        args['globals'] = self._build_global_args()
        args[command] = self._build_command_args(command, flags)
        return args

    @staticmethod
    def _build_command(command, args):
        return 'docker-compose {} {} {}'.format(
            ' '.join(args['globals']), command, ' '.join(args[command])
        )

    def up(self, flags=None):
        """Equivalent to docker-compose up <flags>"""
        args = self._build_args_for('up', flags)
        exit_code, output = self._execute('up', args)
        if exit_code != 0:
            raise RuntimeError('%s: %s', exit_code, output)
        return self._parse_containers(self.options['files'])

    def down(self, flags=None):
        """Equivalent to docker-compose down <flags>"""
        args = self._build_args_for('down', flags)
        return self._execute('down', args, test_success=True)

    def _execute(self, command, args=None, test_success=False):
        command = self._build_command(command, args)
        return util.shell(command, test_success)

    @staticmethod
    def _parse_services(files):
        services = []
        for cfile in files:
            with open(cfile) as fd:
                cf = yaml.safe_load(fd)
            services.extend(cf['services'].keys())
        return list(set(services))

    def _parse_containers(self, files):
        services = self._parse_services(files)
        return [Container(name) for name in services]


class Container:
    """A proxy object representing a docker container."""
    def __init__(self, name, client=None, delay=10):
        self.client = client or docker.from_env()
        self.name = name
        self.delay = delay
        self.obj = self._load_container(name)

    def _load_container(self, name):
        tries = 0
        while True:
            try:
                return self.client.containers.get(name)
            except HTTPError:
                if tries > 10:
                    raise RuntimeError('Container still not ready')
                tries += 1
                time.sleep(tries)

    def __repr__(self):
        return '%s(%s)' % (
            type(self).__name__,
            self.name
        )

    @property
    def network(self):
        """Exposes the docker network name as an object attribute."""
        network = self.inspect['HostConfig']['NetworkMode']
        return self.inspect['NetworkSettings']['Networks'][network]

    @property
    def ip(self):
        """Exposes the container ip address as an object attribute."""
        return self.network['IPAddress']

    @property
    def hostnames(self):
        """Exposes the hostnames of the container as an object attribute."""
        return self.network['Aliases']

    @property
    def env(self):
        """Exposes the container environment as a dict object attribute."""
        return dict(
            [item.split('=') for item in self.inspect['Config']['Env']])

    @property
    def inspect(self):
        """Exposes a dictionary similar to running `docker inspect <name>`."""
        return self.obj.attrs

    def reload(self):
        """Reload the container object using the docker api."""
        self.obj.reload()

    @property
    def health(self):
        """Exposes the health of the container as an object attribute."""
        return self.obj.attrs['State']['Health']['Status']

    @property
    def is_healthy(self):
        """Exposes whether the container status is healthy as a boolean."""
        return self.health == 'healthy'

    def wait(self):
        """Block until container passes health check."""
        while not self.is_healthy:
            time.sleep(self.delay)
            self.reload()

    @property
    def logs(self):
        """Exposes the container logs as an object attribute."""
        return self.obj.logs().decode().strip()

    def exec(self, cmd, test_success=False, output_only=False,
             exit_code_only=False):
        """Executes a command inside the container"""
        if not isinstance(cmd, str):
            cmd = str(cmd)
        exec_id = self.client.api.exec_create(self.name, cmd).get('Id')
        output = self.client.api.exec_start(exec_id).decode().strip()
        exit_code = self.client.api.exec_inspect(exec_id).get('ExitCode')
        if test_success:
            return exit_code == 0
        if output_only:
            return output
        if exit_code_only:
            return exit_code
        return exit_code, output
