import time
import logging
import traceback

from compose.cli import command
from compose.config.errors import ConfigurationError

import logger

from cStringIO import StringIO
import sys


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = sys.stderr = self._out = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._out.getvalue().splitlines())
        del self._out
        sys.stdout = self._stdout
        sys.stderr = self._stderr


class Monitor(object):
    def __init__(self, path, options,
                 norecreate, nodeps, running, filelog=None):
        global log

        if "log" not in globals():
            if filelog is not None:
                log = logging.getLogger(__name__)
                log.addHandler(logger.FileHandler(filelog))
                log.setLevel(logging.DEBUG)
            else:
                log = logging.getLogger(__name__)
                log.addHandler(logger.StreamHandler())
                log.setLevel(logging.DEBUG)

        self.path = path
        self.options = options
        self.norecreate = norecreate
        self.nodeps = nodeps
        self.running = running
        try:
            self.project = command.project_from_options(self.path,
                                                        self.options)
        except ConfigurationError:
            log.error("Can't create a monitor unit\n{}".
                format(traceback.format_exc()))
            raise SystemExit

    def _pullup(self):
        try:
            self.project.pull()
            log.info("Images pulled successfully")
        except Exception:
            log.error("Can't pull images")
            raise

        if self.norecreate:
            return

        if self.running:
            services = self._fully_running_services()
        else:
            services = self.project.services

        if self.nodeps:
            for service in services:
                try:
                    service.execute_convergence_plan(service.convergence_plan())
                    log.info("Service \"{}\" updated successfully".format(service.name))
                except Exception:
                    log.error("Can't update service \"{}\"".format(service.name))
                    raise
        else:
            try:
                self.project.up([el.name for el in services], detached=True)
                log.info("Project updated successfully")
            except Exception:
                log.error("Can't update project")
                raise

    def _fully_running_services(self):
        fully_running = []

        for service in self.project.get_services():
            if all(container.is_running for container in service.containers(stopped=True)):
                fully_running.append(service)
            else:
                log.warning("Some containers for service \"{}\" are down". \
                    format(service.name))

        return fully_running

    def run(self, timeout, scheduler):
        self.project.up(detached=True)
        log.info("Monitor started successfully")
        while True:
            try:
                with Capturing() as output:
                    self._pullup()
            except Exception:
                log.error("Service checking failed\n{}".
                    format(traceback.format_exc()))
            if scheduler:
                break

            log.info("Checked successfully\n{}".format(output))
            time.sleep(timeout)
