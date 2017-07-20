"""Utilities for working with the Docker CLI

We could use the 'docker' package for this, but we want users to be able to
interact with Docker just as they would through the actual CLI. Therefore it
makes more sense to just use the actual Docker CLI, rather than re-implementing
the whole interface.
"""

import pty
import shlex
import distutils.spawn
import subprocess


class DockerCLI(object):
    """Class representing a Docker Command Line Interface."""

    def __init__(self, binary_name='docker'):
        """DockerCLI class constructor.

        binary_name should be a string representing the binary (present in the
        PATH) which can be called as the Docker CLI.
        """

        self.docker_binary = binary_name
        if not self.does_docker_exist():
            raise DockerCLIError('Docker binary "{}" does not exist.'
                                 .format(binary_name))

    def does_docker_exist(self):
        """Test if the given Docker binary actually exists.

        Returns True if the binary exists, False otherwise.
        """

        # Equivalent to running `which docker` and checking the output isn't
        # empty.
        which = distutils.spawn.find_executable(self.docker_binary)
        return which is not None

    def image_exists(self, image):
        """Tests if a given image is installed.

        Returns True if the image is installed, False otherwise.
        """

        # We use the `docker images` command, then format it to show the image
        # repo. If the output is empty, there's no image available.
        args = [
            self.docker_binary,
            'images',
            image,
            '--format',
            '{{.Repository}}'
        ]

        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        return output != b''

    def __build_args(self, image, bind_mounts, environment, docker_args,
                     img_args):
        """Builds an array representing the program to be launched & its
        arguments.

        Returns an array.
        """

        args = [
            self.docker_binary,
            'run',
            '-it'
        ]

        docker_args = shlex.split(docker_args)
        args.extend(docker_args)

        for key, val in bind_mounts.items():
            args.append('-v')
            args.append(''.join([val, ':', key]))

        for key, val in environment.items():
            args.append('-e')
            args.append(''.join([key, '=', val]))

        img_args = shlex.split(img_args)
        args.append(image)
        args.extend(img_args)

        return args

    def run_image(self, image, bind_mounts=None, environment=None,
                  docker_args=None, img_args=None, quiet=False):
        """Runs a given image in a pseudo-terminal.

        bind_mounts should be an object, with keys of locations inside the
        container, and values of locations in the host machine.

        environment should be an object, with keys of environment variable
        names, and values of their values.

        docker_args should be a string of extra arguments to be passed to
        Docker, represented as they would be on the command line.

        img_args should be a string of extra arguments to be passed to Docker,
        represented as they would be on the command line.

        Returns the exit status of the image.
        """

        if not self.image_exists(image):
            raise DockerCLIError('Docker image "{}" does not exist'
                                 .format(image))

        if bind_mounts is None:
            bind_mounts = {}
        if environment is None:
            environment = {}
        if docker_args is None:
            docker_args = ''
        if img_args is None:
            img_args = ''

        args = self.__build_args(image, bind_mounts, environment, docker_args,
                                 img_args)

        if not quiet:
            print('Running command {}'.format(' '.join(args)))

        return pty.spawn(args)


class DockerCLIError(Exception):
    """Class for Docker exceptions."""

    pass
