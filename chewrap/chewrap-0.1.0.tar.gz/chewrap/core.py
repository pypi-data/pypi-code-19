"""Core CheWrap code, which actually runs the command line interface."""

import chewrap.arguments
import chewrap.docker
import chewrap.parser
import chewrap.usage
import sys


class CheWrap(object):
    """Main CheWrap class.

    Runs the command line interface.
    """

    def __init__(self):
        """Class constructor."""

        self.create_parser()
        self.parsed_args = vars(self.parser.parse_args())
        self.create_docker()

    def create_parser(self):
        """Creates a chewrap.parser.ArgumentParser object.

        The ArgumentParser object is used to parse user input on the command
        line.
        """

        self.parser = chewrap.parser.ArgumentParser()
        self.args = chewrap.arguments.get_arguments()
        self.parser.add_argument('-v', '--version', action='version',
                                 version=chewrap.usage.get_program_info())
        self.parser.add_che_args(self.args)

    def create_docker(self):
        """Creates a chewrap.docker.DockerCLI object.

        The DockerCLI object interacts with the Docker Command Line Interface.
        """

        self.docker = chewrap.docker.DockerCLI(self.parsed_args['docker_bin'])

    def run(self):
        """Runs CheWrap."""

        bind_mounts = self.get_bind_mounts()
        env_vars = self.get_environment_vars()
        docker_args = self.get_docker_args()

        if self.parsed_args['omit_socket']:
            bind_mounts.pop('/var/run/docker.sock')

        exit_code = self.docker.run_image(self.parsed_args['che_image'],
                                          bind_mounts, env_vars, docker_args,
                                          self.parsed_args['commands'],
                                          self.parsed_args['quiet'])

        sys.exit(exit_code)

    def get_bind_mounts(self):
        """Returns a dict mapping directories inside the container to the host
        directories they should be bind mounted to."""

        bind_mounts = {}

        for val in chewrap.arguments.get_bind_mounts():
            trimmed_val = chewrap.arguments.sort_args_key(val)

            if self.parsed_args[trimmed_val] is not None:
                container_dir = self.args[val]['containerDirectory']
                bind_mounts[container_dir] = self.parsed_args[trimmed_val]

        return bind_mounts

    def get_environment_vars(self):
        """Returns a dict mapping environment variables inside the container to
        their values."""

        environment_vars = {}

        for val in chewrap.arguments.get_environment_vars():
            trimmed_val = chewrap.arguments.sort_args_key(val)

            if self.parsed_args[trimmed_val] is not None:
                variable = self.args[val]['envVariable']
                environment_vars[variable] = self.parsed_args[trimmed_val]

        return environment_vars

    def get_docker_args(self):
        """Returns a string of options to pass to Docker."""

        docker_args = []

        if not self.parsed_args['preserve_container']:
            docker_args.append('--rm')

        if self.parsed_args['user'] is not None:
            docker_args.append('-u')
            docker_args.append(self.parsed_args['user'])

        if self.parsed_args['docker_opts'] is not None:
            docker_args.append(self.parsed_args['docker_opts'])

        docker_args = ' '.join(docker_args)
        return docker_args
