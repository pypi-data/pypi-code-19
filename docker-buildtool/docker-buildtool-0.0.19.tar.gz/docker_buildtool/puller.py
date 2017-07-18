import os
import logging
import yaml

from pathlib import Path
from docker_buildtool import docker_build, dockerfile, error, utils

logger = logging.getLogger(__name__)

def path(*args):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *args))

class Puller(object):
    def __init__(self, dockerfile):
        self.dockerfile = dockerfile

    def run(self, dryrun):
        if os.path.exists(self.dockerfile):
            spec = dockerfile.DockerfileBuildSpec(self.dockerfile)
            spec.run_setup(dryrun)

            for include in spec.include:
                if not include.installable:
                    continue
                include.install(dryrun=dryrun, build_root=spec.build_root)

        # Pull in the local repo
        utils.execute_command(dryrun, ['git', 'pull', '--rebase'])
