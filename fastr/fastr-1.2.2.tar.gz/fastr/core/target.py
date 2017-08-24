# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The module containing the classes describing the targets.
"""

from abc import ABCMeta, abstractmethod
from collections import deque, namedtuple, Sequence
import datetime
import os
import platform
import psutil
import subprocess
import time
import threading
import shellescape

import isodate
import requests

import fastr
from fastr import exceptions
from fastr.data import url

# Check if docker is available
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

# Check if environment modules are available
try:
    from fastr.execution.environmentmodules import EnvironmentModules
    ENVIRONMENT_MODULES = EnvironmentModules(fastr.config.protected_modules)
    ENVIRONMENT_MODULES_LOADED = True
except exceptions.FastrValueError:
    ENVIRONMENT_MODULES = None
    ENVIRONMENT_MODULES_LOADED = False

try:
    from nipype.interfaces import base as nipypebase
    NIPYPE_AVAILABLE = True
except:
    NIPYPE_AVAILABLE = False

# Monitor interval for profiling
_MONITOR_INTERVAL = 1.0

SystemUsageInfo = namedtuple('SystemUsageInfo', ['timestamp',
                                                 'cpu_percent',
                                                 'vmem',
                                                 'rmem',
                                                 'read_bytes',
                                                 'write_bytes'])


class ProcessUsageCollection(Sequence):
    # It has to be defined in module for pickling purposes
    usage_type = SystemUsageInfo

    def __init__(self):
        self.seconds_info = deque()
        self.minutes_info = []

    def __len__(self):
        return len(self.seconds_info) + len(self.minutes_info)

    def __getitem__(self, item):
        # First look in minutes, then in seconds
        if item < len(self.minutes_info):
            return self.minutes_info[item]._asdict()
        else:
            return self.seconds_info[item - len(self.minutes_info)]._asdict()

    def append(self, value):
        if not isinstance(value, self.usage_type):
            raise ValueError('Cannot add a non {}.usage_type'.format(type(self).__name__))

        self.seconds_info.append(value)

        if len(self.seconds_info) >= 120:
            self.aggregate(60)

    def aggregate(self, number_of_points):
        oldest_data = [self.seconds_info.popleft() for _ in range(number_of_points)]

        timestamp = oldest_data[-1].timestamp
        cpu_percent = sum(x.cpu_percent for x in oldest_data) / len(oldest_data)
        vmem = max(x.vmem for x in oldest_data)
        rmem = max(x.rmem for x in oldest_data)
        read_bytes = oldest_data[-1].read_bytes
        write_bytes = oldest_data[-1].write_bytes

        self.minutes_info.append(self.usage_type(timestamp=timestamp,
                                                 cpu_percent=cpu_percent,
                                                 vmem=vmem,
                                                 rmem=rmem,
                                                 read_bytes=read_bytes,
                                                 write_bytes=write_bytes))


class Target(object):
    """
    The abstract base class for all targets. Execution with a target should
    follow the following pattern:

    >>> with Target() as target:
    ...     target.run_commmand(['sleep', '10'])
    ...     target.run_commmand(['sleep', '10'])
    ...     target.run_commmand(['sleep', '10'])

    The Target context operator will set the correct paths/initialization.
    Within the context command can be ran and when leaving the context the
    target reverts the state before.
    """
    __metaclass__ = ABCMeta

    if NIPYPE_AVAILABLE:
        _NIPYPE_RUN_COMMAND = nipypebase.run_command

        def nipype_run(self, runtime, output, timeout=None, *args, **kwargs):
            """
            A command that has the same signature as the nipype.interfaces.base.run_command

            This adapts the call to the self.run_command that fastr uses for just dispatching
            without environment setting.
            """
            # It is safe to ignore the environment (as it is just a copy)
            # It is safe to ignore cwd (as it is just a copy)
            # See nipype.interfaces.base:974
            fastr.log.info('Running nipype interface using fastr-patched run_command')
            if len(args) > 0:
                fastr.log.warning('Found uncaught args: {}'.format(args))
            if len(kwargs) > 0:
                fastr.log.warning('Found uncaught kwargs: {}'.format(kwargs))

            result = self.run_command(runtime.cmdline.split())

            # Copy the resulting data into the runtime Bunch
            runtime.stdout = result['stdout']
            runtime.stderr = result['stderr']
            runtime.merged = ''
            runtime.returncode = result['returncode']

            return runtime
    else:
        _NIPYPE_RUN_COMMAND = None

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        if NIPYPE_AVAILABLE:
            # Make sure nipype runs via the Target and not just spawn own subprocesses
            nipypebase.run_command = self.nipype_run
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment where needed
        """
        if NIPYPE_AVAILABLE:
            # Reset nipype to work with own run_command
            nipypebase.run_command = self._NIPYPE_RUN_COMMAND

    @abstractmethod
    def run_command(self, command):
        pass


class LocalBinaryTarget(Target):
    """
    A tool target that is a local binary on the system. Can be found using
    environmentmodules or vfs-path on the executing machine
    """

    DYNAMIC_LIBRARY_PATH_DICT = {
        'windows': 'PATH',  # Not Tested
        'linux': 'LD_LIBRARY_PATH',  # Tested
        'darwin': 'DYLD_LIBRARY_PATH',  # Tested
    }

    _platform = platform.system().lower()
    if _platform not in DYNAMIC_LIBRARY_PATH_DICT:
        fastr.log.warning('"Dynamic library path not supported on platform: {}"'.format(_platform))

    def __init__(self, binary, paths=None, environment_variables=None,
                 initscripts=None, modules=None, interpreter=None, **kwargs):
        """
        Define a new local binary target. Must be defined either using paths and optionally environment_variables
        and initscripts, or enviroment modules.
        """
        self.binary = binary
        if modules is None:
            if 'module' in kwargs and kwargs['module'] is not None:
                fastr.log.warning('Using deprecated module in target (modules is new way to do it)')
                self._modules = (kwargs['module'],)
            else:
                self._modules = None
        elif isinstance(modules, str):
            self._modules = (modules.strip(),)
        else:
            self._modules = tuple(x.strip() for x in modules)

        if isinstance(paths, str):
            self._paths = [{'type': 'bin', 'value': paths}]
        elif paths is None and 'location' in kwargs and kwargs['location'] is not None:
            fastr.log.warning('Using deprecated location in target (paths is the new way to do it)')
            self._paths = [{'type': 'bin', 'value': kwargs['location']}]
        else:
            self._paths = paths

        if paths is not None:
            for path_entry in self._paths:
                if not url.isurl(path_entry['value']):
                    path_entry['value'] = os.path.abspath(path_entry['value'])

        if environment_variables is None:
            environment_variables = {}
        self._envvar = environment_variables

        if initscripts is None:
            initscripts = []
        self._init_scripts = initscripts

        self.interpreter = interpreter

        self._roll_back = None

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        super(LocalBinaryTarget, self).__enter__()

        # Create dictionary of possible platforms, to set dynamic labrary path
        # Add check to see if _platform is present in dictionary
        if self._platform in self.DYNAMIC_LIBRARY_PATH_DICT:
            dynamic_library_path = self.DYNAMIC_LIBRARY_PATH_DICT[self._platform]
        else:
            dynamic_library_path = None

        if ENVIRONMENT_MODULES_LOADED and self._modules is not None and len(self._modules) > 0:
            # Clear the enviroment modules and load all required modules
            ENVIRONMENT_MODULES.clear()
            for module_ in self._modules:
                if not ENVIRONMENT_MODULES.isloaded(module_):
                    ENVIRONMENT_MODULES.load(module_)
                    fastr.log.info('loaded module: {}'.format(module_))
            fastr.log.info('LoadedModules: {}'.format(ENVIRONMENT_MODULES.loaded_modules))
        elif self._paths is not None:
            # Prepend PATH and LD_LIBRARY_PATH as required
            self._roll_back = {'PATH': os.environ.get('PATH', None)}

            # Prepend extra paths to PATH
            bin_path = os.environ.get('PATH', None)
            bin_path = [bin_path] if bin_path else []
            extra_path = [x['value'] for x in self._paths if x['type'] == 'bin']
            extra_path = [fastr.vfs.url_to_path(x) if url.isurl(x) else x for x in extra_path]
            fastr.log.info('Adding extra PATH: {}'.format(extra_path))
            os.environ['PATH'] = os.pathsep.join(extra_path + bin_path)

            # Prepend extra paths to LB_LIBRARY_PATH
            extra_ld_library_path = [x['value'] for x in self._paths if x['type'] == 'lib']
            if len(extra_ld_library_path) > 0:
                if dynamic_library_path is None:
                    message = 'Cannot set dynamic library path on platform: {}'.format(self._platform)
                    fastr.log.critical(message)
                    raise exceptions.FastrNotImplementedError(message)

                self._roll_back[dynamic_library_path] = os.environ.get(dynamic_library_path, None)

                lib_path = os.environ.get(dynamic_library_path, None)
                lib_path = [lib_path] if lib_path else []
                extra_ld_library_path = [fastr.vfs.url_to_path(x) if url.isurl(x) else x for x in extra_ld_library_path]

                fastr.log.info('Adding extra LIB: {}'.format(extra_path))
                os.environ[dynamic_library_path] = os.pathsep.join(extra_ld_library_path + lib_path)

            # Set other environment variables as indicated
            for var, value in self._envvar.items():
                if var in ['PATH', dynamic_library_path]:
                    continue

                self._roll_back[var] = os.environ.get(var, None)
                os.environ = value

            # Run init script(s) if required
            for script in self._init_scripts:
                if isinstance(script, str):
                    script = [script]

                subprocess.call(script)
        else:
            raise exceptions.FastrNotImplementedError(
                'Binary targets must have either paths or modules set! (binary {})'.format(self.binary)
            )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment
        """
        if ENVIRONMENT_MODULES_LOADED and self._modules is not None and len(self._modules) > 0:
            ENVIRONMENT_MODULES.clear()
        elif self._roll_back is not None:
            for var, value in self._roll_back.items():
                if value is not None:
                    os.environ[var] = value
                else:
                    del os.environ[var]

            self._roll_back = None

    def call_subprocess(self, command):
        """
        Call a subprocess with logging/timing/profiling

        :param list command: the command to execute
        :return: execution info
        :rtype: dict
        """
        sysuse = ProcessUsageCollection()
        start_time = time.time()
        fastr.log.info('Calling command arguments: {}'.format(command))
        printable_command = []
        for item in command:
            printable_command.append(shellescape.quote(item))
        fastr.log.info('Calling command: "{}"'.format(' '.join(printable_command)))
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        except OSError as exception:
            if exception.errno == 2:
                raise exceptions.FastrExecutableNotFoundError(command[0])
            elif exception.errno == 13:
                # Permission denied
                raise exceptions.FastrNotExecutableError('Cannot execute {}, permission denied!'.format(command[0]))
            else:
                raise exception
        monitor_thread = threading.Thread(target=self.monitor_process, name='SubprocessMonitor', args=(process, sysuse))
        monitor_thread.daemon = True  # Make sure this Thread does not block exiting the script
        monitor_thread.start()
        stdout, stderr = process.communicate()
        return_code = process.poll()
        end_time = time.time()

        if monitor_thread.is_alive():
            monitor_thread.join(2 * _MONITOR_INTERVAL)
            if monitor_thread.is_alive():
                fastr.log.warning('Ignoring unresponsive monitor thread!')

        return {'returncode': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'command': command,
                'resource_usage': list(sysuse),
                'time_elapsed': end_time - start_time}

    def monitor_process(self, process, resources):
        """
        Monitor a process and profile the cpu, memory and io use. Register the
        resource use every _MONITOR_INTERVAL seconds.

        :param subproces.Popen process: process to monitor
        :param resources: list to append measurements to
        """
        psproc = psutil.Process(process.pid)

        # Loop initialization
        psproc.cpu_percent()  # Get rid of meaningless 0.0 at start
        last_timestamp = datetime.datetime.utcnow()

        while process.poll() is None:
            try:
                # The sleep duration is adapted to loop duration so aggregation will not cause
                # extended intervals
                sleep_duration = _MONITOR_INTERVAL - (datetime.datetime.utcnow() - last_timestamp).total_seconds()
                sleep_duration = 0.0 if sleep_duration < 0.0 else sleep_duration
                time.sleep(sleep_duration)

                # Get process usage information
                memory_info = psproc.memory_info()

                if self._platform == 'darwin':
                    io_read = None
                    io_write = None
                else:
                    io_info = psproc.io_counters()
                    io_read = io_info.read_bytes
                    io_write = io_info.write_bytes

                last_timestamp = datetime.datetime.utcnow()
                usage = resources.usage_type(timestamp=last_timestamp.isoformat(),
                                             cpu_percent=psproc.cpu_percent(),
                                             vmem=memory_info.vms,
                                             rmem=memory_info.rss,
                                             read_bytes=io_read,
                                             write_bytes=io_write)

                resources.append(usage)

            except psutil.Error:
                # If the error occured because during the interval of meassuring the CPU use
                # the process stopped, we do not mind
                if process.poll() is None:
                    raise

    def run_command(self, command):
        if self.interpreter is not None:
            paths = [x['value'] for x in self._paths if x['type'] == 'bin']
            fastr.log.info('Options: {}'.format(paths))
            containing_path = next(x for x in paths if os.path.exists(os.path.join(x, command[0])))
            command = [self.interpreter, os.path.join(containing_path, command[0])] + command[1:]

        fastr.log.debug('COMMAND: "{}" ({})'.format(command, type(command).__name__))
        return self.call_subprocess(command)


class DockerTarget(Target):
    """
    A tool target that is located in a Docker images. Can be run using
    docker-py.
    """
    def __init__(self, binary, docker_image):
        """
        Define a new docker target.

        :param str docker_image: Docker image to use
        """
        if not DOCKER_AVAILABLE:
            raise exceptions.FastrOptionalModuleNotAvailableError('Target cannot be used, module "docker" unavailable')

        self.binary = binary
        self._docker_image = docker_image

        #: Docker api to use for docker target
        self.docker_api = 'unix://var/run/docker.sock'

        self._docker_client = docker.DockerClient(base_url=self.docker_api,
                                                  version='auto')
        self._container = None

    def __enter__(self):
        super(DockerTarget, self).__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self._container = None

    @property
    def container(self):
        return self._container

    def run_command(self, command):
        # Bind all fastr mounts
        mounts = fastr.config.mounts.values()
        fastr.log.info('DOCKER MOUNTS: {}'.format(mounts))
        binds = {x: {'bind': x, 'mode': 'ro'} for x in mounts if os.path.exists(x)}
        binds[fastr.config.mounts['tmp']]['mode'] = 'rw'
        fastr.log.info('DOCKER BINDS: {}'.format(binds))

        fastr.log.info('DOCKER CREATE CONTAINER')
        container = self._docker_client.containers.run(
            image=self._docker_image,
            command=command,
            detach=True,
            volumes=binds,
            network_disabled=True,
            user='{}:{}'.format(os.getuid(), os.getgid()),
            working_dir=os.path.abspath(os.curdir),
            environment=os.environ,
        )

        # Start monitoring
        sysuse = ProcessUsageCollection()
        monitor_thread = threading.Thread(target=self.monitor_docker,
                                          name='DockerMonitor',
                                          args=(container, sysuse))
        monitor_thread.daemon = True  # Make sure this Thread does not block exiting the script
        monitor_thread.start()
        start_time = time.time()

        # Run docker container
        fastr.log.info('DOCKER WAIT')
        return_code = container.wait()
        fastr.log.info('DOCKER WAIT DONE')
        end_time = time.time()
        stdout = container.logs(stdout=True, stderr=False, stream=False, timestamps=True)
        stderr = container.logs(stdout=False, stderr=True, stream=False, timestamps=True)

        if monitor_thread.is_alive():
            monitor_thread.join(2 * _MONITOR_INTERVAL)
            if monitor_thread.is_alive():
                fastr.log.warning('Ignoring unresponsive monitor thread!')

        # Clean the contianer
        container.remove()

        return {'returncode': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'command': command,
                'resource_usage': list(sysuse),
                'time_elapsed': end_time - start_time}

    def monitor_docker(self, container, resources):
        """
        Monitor a process and profile the cpu, memory and io use. Register the
        resource use every _MONITOR_INTERVAL seconds.

        :param subproces.Popen process: process to monitor
        :param resources: list to append measurements to
        """
        try:
            for stat in container.stats(stream=True,
                                        decode=True):

                # Get cpu, memory and io statistics
                timestamp = isodate.isodatetime.parse_datetime(stat['read'])
                usage = resources.usage_type(timestamp=timestamp.isoformat(),
                                             cpu_percent=stat['cpu_stats']['cpu_usage']['total_usage'],
                                             vmem=-1.0,
                                             rmem=stat['memory_stats']['rss'],
                                             read_bytes=0.0,
                                             write_bytes=0.0)

                resources.append(usage)
        except requests.exceptions.ReadTimeout:
            fastr.log.info('Docker Monitor timed out')

