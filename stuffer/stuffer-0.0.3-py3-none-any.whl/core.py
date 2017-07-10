import abc
import logging
import subprocess
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from stuffer.utils import NaturalReprMixin, str_split


class Action(NaturalReprMixin):
    """Base class for all actions to be taken."""

    __metaclass__ = abc.ABCMeta

    _registry = []

    @classmethod
    def registered(cls):
        return list(cls._registry)

    def __init__(self):
        self._registry.append(self)
        logging.debug("Registered action: {}".format(self))

    def execute(self):
        logging.info("Executing {}".format(self))
        for prereq in self.prerequisites():
            prereq.run()
        self.run()

    def prerequisites(self):
        return []

    def command(self):
        pass

    def use_shell(self):
        return False

    @staticmethod
    def tmp_dir():
        return Path("/tmp/stuffer_tmp")

    def run(self):
        cmd = self.command() if self.use_shell() else str_split(self.command())
        return run_cmd(cmd, shell=self.use_shell())

    def _extract_net_archive(self, uri, destination):
        # TODO: Verify checksum
        # noinspection PyUnresolvedReferences
        archive_name = Path(urlparse(uri).path).parts[-1]
        if not destination.is_dir():
            destination.mkdir(parents=True)
        local_archive = self.tmp_dir() / archive_name
        if not local_archive.exists():
            run_cmd(["wget", "--output-document", str(local_archive), uri])
        run_cmd(["tar", "--directory", str(destination), "-xf", str(local_archive)])


class Group(Action):
    @abc.abstractmethod
    def children(self) -> List[Action]:
        raise NotImplementedError()

    def run(self):
        for child in self.children():
            child.execute()


def run_cmd(cmd, *args, **kwargs):
    joined = " ".join(str_split(cmd))
    logging.info("> %s", joined)
    try:
        output_bytes = subprocess.check_output(cmd, *args, **kwargs)
        output = output_bytes.decode(encoding="ascii", errors="ignore")
        logging.debug(output)
        return output
    except subprocess.CalledProcessError as err:
        logging.error("Command %s failed:\n%s", joined, str(err.output))
        raise
