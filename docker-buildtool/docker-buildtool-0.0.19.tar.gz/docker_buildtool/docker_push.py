import logging

from docker_buildtool import utils

logger = logging.getLogger(__name__)


class DockerPush(object):
    def __init__(self, image):
        self.image = image

    def run(self, dryrun=False):
        utils.execute_command(dryrun, ['docker', 'push', self.image])
