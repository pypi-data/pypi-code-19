# -*- coding: utf-8 -*-

from __future__ import division, print_function
import atexit
import drmaa
import logging
import os
import sys
from collections import defaultdict
from jug import init as juginit, task as jugtask
from jug.subcommands import SubCommand
from math import ceil
from random import shuffle
from time import time, sleep
from .errors import UnsupportedDRMAAVersion, UnrecognizedQueueSystem, JobFailed
from .queues import SystemSGE, SystemSLURM, SystemLSF
from .queues import SYSTEM_SGE, SYSTEM_GE, SYSTEM_SLURM, SYSTEM_LSF

# TODO
# * SLURM's reference http://apps.man.poznan.pl/trac/slurm-drmaa#Nativespecification
# * LSF https://github.com/PlatformLSF/lsf-drmaa (a nice table on the README under "Native Specification")
# * SGE - man qsub (i.e. -pe smp 8 -c 10 ... )
# * Possibly replace drmaa with gc3pie

__all__ = [
    "ScheduleCommand",
]


class Job(object):
    SLOT = {
        "free": set((
            drmaa.JobState.DONE,
            drmaa.JobState.FAILED,
        )),
        "queue": set((
            drmaa.JobState.UNDETERMINED,
            drmaa.JobState.QUEUED_ACTIVE,
        )),
        "hold": set((
            drmaa.JobState.SYSTEM_ON_HOLD,
            drmaa.JobState.USER_ON_HOLD,
            drmaa.JobState.USER_SYSTEM_ON_HOLD,
        )),
        "suspend": set((
            drmaa.JobState.SYSTEM_SUSPENDED,
            drmaa.JobState.USER_SUSPENDED,
        )),
        "run": set((
            drmaa.JobState.RUNNING,
        )),
    }

    def __init__(self, session, jobid):
        self.jobid = jobid
        self.session = session

    def reap(self):
        """Collect job info if it has already finished.

        Returns None if info is not available (usually job still active)

        Calling this function is necessary to obtain job statistics from the
        DRMAA session. Collecting this info will also avoid a memory leak
        """
        return self.session.wait(self.jobid, self.session.TIMEOUT_NO_WAIT)

    def wait(self):
        return self.session.wait(self.jobid, self.session.TIMEOUT_WAIT_FOREVER)

    def kill(self):
        """Kills the specified job
        """
        try:
            self.session.control(self.jobid, drmaa.JobControlAction.TERMINATE)
        except (drmaa.errors.InternalException, drmaa.errors.InvalidJobException):
            # Job may have died already
            pass

    def _get_status(self, category):
        status = self.session.jobStatus(self.jobid)
        return status in self.SLOT[category]

    def is_done(self):
        return self._get_status("free")

    def is_queued(self):
        return self._get_status("queue")

    def is_held(self):
        return self._get_status("hold")

    def is_suspended(self):
        return self._get_status("suspend")

    def is_active(self):
        return self._get_status("active")


class SessionHandler(object):

    def __init__(self, options, store):
        # target: {job, job}
        self.assigned = defaultdict(set)
        # target: status: nr_of_jobs
        self.status = defaultdict(lambda: defaultdict(int))
        self.task_resources = {}

        self.used_jobs = 0
        self.store = store
        self.jugfile = options.jugfile
        self.jugdir = options.jugdir
        self.max_jobs = options.schedule_max_jobs
        self.script = options.schedule_script
        self.logs = options.schedule_logs
        self.continue_on_error = options.schedule_continue_on_error

        self.s = drmaa.Session()
        self.s.initialize()
        atexit.register(lambda s: s.exit(), self.s)

        self.check_version()
        self._system = None
        self._identify_system()

    def _identify_system(self):
        if SYSTEM_SLURM in self.s.drmsInfo:
            self._system = SystemSLURM()
        elif SYSTEM_LSF in self.s.drmsInfo:
            self._system = SystemLSF()
        elif SYSTEM_SGE in self.s.drmsInfo or SYSTEM_GE in self.s.drmsInfo:
            self._system = SystemSGE()
        else:
            raise UnrecognizedQueueSystem(self.s.contact, self.s.drmsInfo,
                                          self.s.drmaaImplementation, self.s.version)

        logging.debug("Identified cluster system '%s'", self._system)

    def info(self):
        logging.info("Supported contact strings: %s", self.s.contact)
        logging.info("Supported DRM systems: %s", self.s.drmsInfo)
        logging.info("Supported DRMAA implementations: %s", self.s.drmaaImplementation)
        logging.info("Version %s", self.s.version)

    def check_version(self):
        if self.s.version.major != 1:
            raise UnsupportedDRMAAVersion(self.s.version)

    def is_complete(self):
        complete = True

        for target in self.status:
            ready = self.status[target]["ready"]
            wait = self.status[target]["wait"]
            active = self.status[target]["active"]
            if ready + wait + active > 0:
                complete = False
                break

        return complete

    def _add_job(self, target, jobid):
        # Create a job instance
        job = Job(self.s, jobid)

        self.assigned[target].add(job)
        self.used_jobs += 1

    def _rm_job(self, target, job):
        self.assigned[target].remove(job)
        self.used_jobs -= 1

    def launch_job(self, jobtemplate, bulk=0):
        try:
            if bulk > 1:
                return self.s.runBulkJobs(jobtemplate, beginIndex=1, endIndex=bulk, step=1)
            else:
                return self.s.runJob(jobtemplate)
        except drmaa.errors.DrmaaException as e:
            logging.error("An error happened while submitting job(s) from "
                          "target %s to the queue", jobtemplate.jobName)
            logging.exception(e)
            raise JobFailed()

    def run(self, target, jobs=1, wait_cycles=8, wait_cycle_time=15):
        logging.info("Starting %s jobs on target %s", jobs, target)

        jt = self.s.createJobTemplate()
        jt.remoteCommand = self.script
        jt.args = ["execute", self.jugfile,
                   "--target", target,
                   "--jugdir", self.jugdir,
                   "--nr-wait-cycles", str(wait_cycles),
                   "--wait-cycle-time", str(wait_cycle_time)]
        jt.jobName = target
        jt.jobEnvironment = os.environ.copy()
        jt.workingDirectory = os.getcwd()

        # Construct jt.nativeSpecification with specified resources
        res = self._system.native_resources(self.task_resources[target])
        logging.debug("Job will be submitted with the following resources '%s'", res)
        jt.nativeSpecification = res

        # NOTE: We need a colon as a prefix for output/errorPath. Weird DRMAA requirement
        if self._system.is_slurm():
            logging.debug("SLURM requires an explicit filename for output logs")
            # Currently only SLURM suffers from this
            # SGE and LSF can recognize a path and keep default filename
            jt.outputPath = ":" + os.path.join(self.logs, "jug-%A_%a.out")
            jt.errorPath = ":" + os.path.join(self.logs, "jug-%A_%a.err")
        else:
            # join an empty '' to ensure we get a trailing slash
            jt.outputPath = ":" + os.path.join(self.logs, '')
            jt.errorPath = jt.outputPath

        logging.debug("Running %s with %s and logs to %s", jt.remoteCommand, jt.args, jt.outputPath)

        if jobs == 1:
            jobid = self.launch_job(jt)
            self._add_job(target, jobid)
        else:
            if self._system.is_slurm():
                logging.warning(
                    "If you see a segmentation fault just after this warning, "
                    "check https://git.io/vQzY7 and contact your cluster administrator "
                    "to update libdrmaa.so to the latest available from: "
                    "http://apps.man.poznan.pl/trac/slurm-drmaa/downloads"
                )

            jobids = self.launch_job(jt, jobs)

            for jobid in jobids:
                self._add_job(target, jobid)

        self.s.deleteJobTemplate(jt)

        return jobid

    def collect_jobs(self):
        """Collect jobs that have ended and update existing slots accordingly
        """
        for target in self.assigned:
            for job in self.assigned[target].copy():
                if job.is_done():
                    jobinfo = job.reap()
                    logging.info("Reaped a jug instance from target %s - a queued job finished", target)

                    self._rm_job(target, job)

                    if jobinfo.exitStatus or jobinfo.wasAborted or jobinfo.hasSignal:
                        logging.error("One jug instance failed with exit code %s , abort status %s "
                                      "and signal %s. Check %s for more information",
                                      jobinfo.exitStatus, jobinfo.wasAborted, jobinfo.terminatedSignal, self.logs)
                        logging.error("Additional job information: %s", jobinfo)
                        # If a job fails discard one slot
                        self.max_jobs -= 1

                        if not self.continue_on_error:
                            raise JobFailed()
                    else:
                        logging.debug("One jug instance ended successfully. Additional job information: %s", jobinfo)

    def update_status(self):
        """Computes the number of tasks in each status and how tasks are grouped
        as targets, taking into account their dependency graph
        """
        # Whenever we update the status of the project we also need to recompute
        # the targets because new tasks under new targets may now be available
        status = self.status
        status.clear()

        # And update what resources are to be allocated to each task set
        resources = self.task_resources
        resources.clear()

        # Reinitialize jug's task listing to ensure newly available tasks are picked up
        del jugtask.alltasks[:]
        self.store, jugspace = juginit(self.jugfile, self.jugdir, store=self.store)

        for task in jugtask.alltasks:
            task_target = task.name
            try:
                resources[task_target] = task._resources
            except AttributeError:
                # Tasks not decorated with ResourcesTaskGenerator
                resources[task_target] = {}

            if task.is_locked():
                status[task_target]["active"] += 1
            elif task.can_load():
                status[task_target]["done"] += 1
            elif task.can_run():
                status[task_target]["ready"] += 1
            else:
                status[task_target]["wait"] += 1

        logging.debug("Internal status is %s", status)

    def assign_jobs(self):
        """Distribute available jobs between targets taking into account how
        many jobs were already assigned to a given target

        At most 50% of available jobs (rounded up) are distributed each iteration
        """
        total_pending = 0
        available_jobs = int(ceil((self.max_jobs - self.used_jobs) / 2))

        if available_jobs == 0:
            logging.info("All job slots are in use (%s) or we are out of slots - No new jobs queued", self.used_jobs)
            return

        allocation = {}

        for target in self.status:
            active = self.status[target]["active"]
            ready = self.status[target]["ready"]
            assigned = len(self.assigned[target])

            pending = ready

            working = assigned - active
            # working can be negative if jug processes are active due to something
            # external to this scheduler. The most common scenario would be a
            # restarted scheduler that left locked (active) jobs behind.

            if working > 0:
                pending -= working

            if pending < 0:
                # Enough jobs have been assigned already, just wait for them to complete
                pending = 0

            total_pending += pending
            allocation[target] = pending

        if total_pending == 0:
            logging.info("All work is taken or complete - No new jobs queued")
            return

        # Compute distribution of jobs
        assigned = 0
        for target in allocation:
            allocation[target] = alloc = int(available_jobs * allocation[target] / total_pending)
            assigned += alloc

        # With small numbers of available_jobs we may end up with ties or other
        # situations where nothing would be distributed. In this case pick
        # a random target that still has some work to be consumed.
        # Ties will eventually resolve themselves
        remaining = available_jobs - assigned

        all_targets = list(allocation.keys())

        while remaining > 0:
            logging.debug("Got %s unassigned jobs, randomly distributing", remaining)
            shuffle(all_targets)

            # If we managed to assign something this iteration
            assigned = False

            for target in all_targets:
                if self.status[target]["ready"] - allocation[target] > 0:
                    allocation[target] += 1
                    remaining -= 1
                    assigned = True

                    if remaining == 0:
                        break

            # We didn't assign anything which means all work is taken
            if not assigned:
                logging.debug("%s jobs without work. Leaving them for next iteration", remaining)
                break

        logging.debug("This iteration job allocation was: %s", allocation)

        # Finally start the jobs
        for target, jobs in allocation.items():
            if jobs > 0:
                self.run(target, jobs)

    def keep_going(self):
        """Returns True unless all work is done or all jobs failed
        """
        self.update_status()

        # All jobs died, or all work is complete.
        # Also only quit when all active jobs ended
        if (self.max_jobs < 1 or self.is_complete()) and self.used_jobs == 0:
            return False

        return True

    def manage_jobs(self):
        # update_status() was already executed by keep_going()
        self.collect_jobs()
        self.assign_jobs()

    def terminate(self, wait=False):
        for target in self.assigned:
            for job in self.assigned[target].copy():
                if wait:
                    job.wait()
                else:
                    job.kill()


def main(session, cycles):
    while session.keep_going():
        start = time()
        session.manage_jobs()

        delta = time() - start

        if delta > cycles:
            delta = 0
        else:
            delta = round(cycles - delta, 1)

        logging.info("Sleeping for %s seconds", delta)
        sleep(delta)


def abort(session):
    sys.stderr.write("Received Ctrl+C / SIGINT, killing all queued jobs\n")
    # Kill all queued jobs
    session.terminate()


class ScheduleCommand(SubCommand):
    """Schedules jobs on a DRMAA compatible queue
    """
    name = "schedule"

    def run(self, store, options, *args, **kwargs):
        # Create the folder where jug log_files will be written
        logs = options.schedule_logs

        if not os.path.isdir(logs):
            os.mkdir(logs)

        s = SessionHandler(options, store)
        s.info()

        try:
            main(s, options.schedule_cycle)
        except KeyboardInterrupt:
            abort(s)
        except JobFailed:
            sys.stderr.write("One or more jobs exited with errors\n")
            sys.stderr.write("Scheduler will now abort\n")
            sys.stderr.write("Waiting for active jobs to finish\n")
            try:
                s.terminate(wait=True)
            except KeyboardInterrupt:
                abort(s)

    def parse(self, parser):
        defaults = self.parse_defaults()

        parser.add_argument("--script", action="store",
                            dest="schedule_script",
                            help=("Script to use instead of '{schedule_script}'. "
                                  "Use this if your cluster environment needs to "
                                  "be setup before execution""".format(**defaults)))
        parser.add_argument("--max-jobs", action="store", type=int,
                            dest="schedule_max_jobs", metavar="MAX_JOBS",
                            help=("Maximum number of jobs to queue "
                                  "(Default: {schedule_max_jobs})".format(**defaults)))
        parser.add_argument("--logs", action="store", dest="schedule_logs",
                            metavar="LOGS",
                            help=("Location to store logs from the queueing system "
                                  "(Default: '{schedule_logs}')".format(**defaults)))
        parser.add_argument("--cycle-time", action="store", type=int,
                            dest="schedule_cycle", metavar="CYCLE_TIME",
                            help=("Number of seconds between each queue action "
                                  "(Default: {schedule_cycle})".format(**defaults)))
        parser.add_argument("--continue-on-error", action="store_const", const="True",
                            dest="schedule_continue_on_error",
                            help="If a job fails, continue until all jobs fail")

    def parse_defaults(self):
        return {
            "schedule_max_jobs": 20,
            "schedule_logs": "jug_logs",
            "schedule_cycle": 60,
            "schedule_continue_on_error": False,
            "schedule_script": sys.argv[0] if sys.argv[0].startswith("/") else "jug",
        }


# vim: ai sts=4 et sw=4
