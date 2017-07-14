"""
The docker tool provides ``build``, ``push`` and ``publish`` commands.

The `build` tasks build the dockerfile and tags the resulting image with the
project's name.
"""
import argparse
import logging

from functools import reduce

from menhir.tool import Tool
from menhir.tool_utils import (
    OK, FAIL, NOTHING_TO_DO,
    argv_to_dict, tool_env, working_dir
)
from menhir.utils import multi, method

log = logging.getLogger(__name__)


def tool():
    return Docker()


class Docker(Tool):

    def name(arg):
        return "docker"

    def dir_info(tool, path, info):
        from os.path import exists, join
        path = join(path, 'Dockerfile')
        has_dockerfile = exists(path)
        return {
            'project_recognised': has_dockerfile,
            'can_run': has_dockerfile,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        from os.path import exists, join
        from menhir.tool_utils import run_if

        phase_name = args.phase

        dockerfile = join(path, 'Dockerfile')

        if not exists(dockerfile):
            log.debug(
                'No Dockerfile %(dockerfile)s',
                {'dockerfile': dockerfile})
            return NOTHING_TO_DO

        run_flag = (
            'changed' not in info or
            info['changed'].get('self') or
            info['changed'].get('dependents')
        )

        if phase_name in {'build', 'push', 'publish'}:
            with run_if(run_flag, phase_name, path) as flag:
                if flag:
                    return task(phase_name, path, info, args)
                return OK
        else:
            return NOTHING_TO_DO


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to build and push docker images.",
        **kwargs
    )
    parsers = parser.add_subparsers(help="Docker commands", dest='phase')
    p = parsers.add_parser(
        'build',
        help='Build a docker image from a Dockerfile'
    )
    p.add_argument(
        '--build-arg', dest='build_args', action='append',
        help="Specify a build argument for the docker build")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'push',
        help='Push a docker image to a remote repository'
    )
    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the encryption settings")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'publish',
        help='Build and push a docker image to a remote repository'
    )
    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the encryption settings")
    p.add_argument(
        '--build-arg', dest='build_args', action='append',
        help="Specify a build argument for the docker build")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(phase_name, path, info, args):
    return phase_name


@method(task)
def task_default(phase_name, path, info, args):
    return NOTHING_TO_DO


@method(task)
def task_publish(phase_name, path, info, args):
    res = task('build', path, info, args)
    if res != OK:
        return res
    return task('push', path, info, args)


@method(task, 'build')
def docker_build(phase_name, path, info, args):
    from menhir.tool_utils import call, package_script
    log.info('Running docker-build in %s', path)

    project_name = info['project-name']

    env = tool_env()
    env['MENHIR_TAG'] = project_name

    build_args = reduce(
        lambda v, a: v + ['--build-arg', a],
        args.build_args or [],
        [])

    with package_script("/tools/docker/docker-build.sh") as f:
        with working_dir(path):
            return call([f.name] + build_args, env=env,)


@method(task, 'push')
def docker_push(phase_name, path, info, args):
    from menhir.project import branch, image
    from menhir.tool_utils import call, package_script, slugify
    log.info('Running docker-push in %s', path)

    arg_names = info.get('docker', {}).get('args', [])
    arg_values = args.args or []

    arg_dict = argv_to_dict(arg_names, arg_values)
    if arg_dict is None:
        log.error('Expected --arg for each of %s', arg_names)
        return FAIL

    project_name = info['project-name']
    current_branch = branch()
    tag = project_name
    sha_tag = image(info, path)
    sha_tag = sha_tag % arg_dict
    if not sha_tag:
        log.error('No remote repository configured to push to.')
        return FAIL
    branch_tag = "%s:%s" % (
        sha_tag.split(':')[0],
        slugify(current_branch, length=40),
    )
    branch_tag = branch_tag % arg_dict

    env = tool_env()
    env['MENHIR_TAG'] = tag
    env['MENHIR_BRANCH_TAG'] = branch_tag
    env['MENHIR_SHA_TAG'] = sha_tag

    with package_script("/tools/docker/docker-push.sh") as f:
        with working_dir(path):
            return call([f.name], env=env,)
