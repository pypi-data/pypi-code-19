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

import copy
import os
import Queue
import sys
import threading

import fastr
from fastr import exceptions
from fastr.core.baseplugin import PluginState

try:
    import drmaa
    load_drmaa = True
except (ImportError, RuntimeError):
    load_drmaa = False

from fastr.execution.job import JobState
from fastr.execution.executionpluginmanager import ExecutionPlugin
from fastr.utils.classproperty import classproperty


class FastrDRMAANotFoundError(exceptions.FastrImportError):
    """
    Indicate the DRMAA module was not found on the system.
    """
    pass


class FastrDRMAANotFunctionalError(exceptions.FastrError):
    """
    Indicate DRMAA is found but creating a session did not work
    """
    pass


class DRMAAExecution(ExecutionPlugin):
    """
    A DRMAA execution plugin to execute Jobs on a Grid Engine cluster. It uses
    a configuration option for selecting the queue to submit to. It uses the
    python ``drmaa`` package.

    .. note::

        To use this plugin, make sure the ``drmaa`` package is installed and
        that the execution is started on an SGE submit host with DRMAA
        libraries installed.

    .. note::

        This plugin is at the moment tailored to SGE, but it should be fairly
        easy to make different subclasses for different DRMAA supporting
        systems.
    """
    if not load_drmaa:
        _status = (PluginState.failed, 'Could not load DRMAA module required for cluster communication')

    # DRMAA Supports cancelling jobs, job dependencies and hold release actions
    SUPPORTS_CANCEL = True
    SUPPORTS_DEPENDENCY = True
    SUPPORTS_HOLD_RELEASE = True
    CANCELS_DEPENDENCIES = False

    def __init__(self, finished_callback=None, cancelled_callback=None, status_callback=None):
        super(DRMAAExecution, self).__init__(finished_callback, cancelled_callback, status_callback)

        # Some default
        self.default_queue = fastr.config.drmaa_queue

        # Create the DRMAA session
        try:
            self.session = drmaa.Session()
            self.session.initialize()
        except drmaa.errors.DrmaaException as exception:
            raise FastrDRMAANotFunctionalError('Encountered an error when creating DRMAA session: [{}] {}'.format(
                exception.__class__,
                str(exception)
            ))

        fastr.log.debug('A DRMAA session was started successfully')
        response = self.session.contact
        fastr.log.debug('session contact returns: ' + response)

        # Create job translation table
        self.job_translation_table = dict()
        self.job_lookup_table = dict()

        # Create even queue lock
        self.submit_queue = Queue.Queue()
        self.queue_lock = threading.Event()

        # Create callback collector and job submitter
        self.running = True
        fastr.log.debug('Creating job collector')
        self.collector = threading.Thread(name='DRMAAJobCollector-0', target=self.collect_jobs, args=())
        self.collector.daemon = True
        fastr.log.debug('Starting job collector')
        self.collector.start()

        fastr.log.debug('Creating job submitter')
        self.submitter = threading.Thread(name='DRMAAJobSubmitter-0', target=self.submit_jobs, args=())
        self.submitter.daemon = True
        fastr.log.debug('Starting job submitter')
        self.submitter.start()

    @classproperty
    def configuration_fields(cls):
        return {
            "drmaa_queue": (str, "week", "The default queue to use for jobs send to the scheduler")
        }

    @classmethod
    def test(cls):
        if not load_drmaa:
            raise FastrDRMAANotFoundError('Could not import the required drmaa for this plugin')

    def cleanup(self):
        # Stop submissions and callbacks
        self.running = False  # Signal collector thread to stop running
        super(DRMAAExecution, self).cleanup()

        # See if there are leftovers in the job translation table that can be cancelled
        while len(self.job_translation_table) > 0:
            drmaa_job_id, job = self.job_translation_table.popitem()
            fastr.log.info('Terminating left-over job {}'.format(drmaa_job_id))
            self.session.control(drmaa_job_id, 'terminate')

        fastr.log.debug('Stopping DRMAA executor')
        # Destroy DRMAA
        try:
            self.session.exit()
            fastr.log.debug('Exiting DRMAA session')
        except drmaa.NoActiveSessionException:
            pass
        if self.collector.isAlive():
            fastr.log.debug('Terminating job collector thread')
            self.collector.join()
        if self.submitter.isAlive():
            fastr.log.debug('Terminating job submitter thread')
            self.submitter.join()
        fastr.log.debug('DRMAA executor stopped!')

    def _queue_job(self, job):
        self.submit_queue.put(job, block=True)

    def _cancel_job(self, job):
        try:
            drmaa_job_id = self.job_lookup_table.pop(job.id)
        except KeyError:
            fastr.log.info('Job {} not found in DRMAA lookup'.format(job.id))
            return

        fastr.log.debug('Cancelling job {}'.format(drmaa_job_id))
        try:
            self.session.control(drmaa_job_id, drmaa.JobControlAction.TERMINATE)
        except drmaa.InvalidJobException:
            fastr.log.warning('Trying to cancel an unknown job, already finished/cancelled?')

        try:
            del self.job_translation_table[drmaa_job_id]
        except KeyError:
            pass  # This job is already gone

    def _release_job(self, job):
        drmaa_job_id = self.job_lookup_table[job.id]
        self.session.control(drmaa_job_id, drmaa.JobControlAction.RELEASE)

    def _job_finished(self, result):
        pass

    # FIXME This needs to be more generic! This is for our SGE cluster only!
    def send_job(self, command, arguments, queue=None, walltime=None,
                 job_name=None, memory=None, ncores=None, joinLogFiles=False,
                 outputLog=None, errorLog=None, hold_job=None, hold=False):

        # Create job template
        jt = self.session.createJobTemplate()
        jt.remoteCommand = command

        jt.args = arguments
        jt.joinFiles = joinLogFiles
        env = os.environ
        # Make sure environment modules do not annoy use with bash warnings
        # after the shellshock bug was fixed
        env.pop('BASH_FUNC_module()', None)
        jt.jobEnvironment = env

        if queue is None:
            queue = self.default_queue

        native_spec = '-cwd -q %s' % queue

        if walltime is not None:
            native_spec += ' -l h_rt=%s' % walltime

        if memory is not None:
            native_spec += ' -l h_vmem=%s' % memory

        if ncores is not None:
            native_spec += ' -pe smp %d' % ncores

        if outputLog is not None:
            native_spec += ' -o %s' % outputLog

        if errorLog is not None:
            native_spec += ' -e %s' % errorLog

        if hold_job is not None:
            if isinstance(hold_job, int):
                native_spec += ' -hold_jid {}'.format(hold_job)
            elif isinstance(hold_job, list) or isinstance(hold_job, tuple):
                if len(hold_job) > 0:
                    jid_list = ','.join([str(x) for x in hold_job])
                    native_spec += ' -hold_jid {}'.format(jid_list)
            else:
                fastr.log.error('Incorrect hold_job type!')

        if hold:
            # Add a user hold to the job
            native_spec += ' -h'

        fastr.log.debug('Setting native spec to: {}'.format(native_spec))
        jt.nativeSpecification = native_spec
        if job_name is None:
            job_name = command
            job_name = job_name.replace(' ', '_')
            job_name = job_name.replace('"', '')
            if len(job_name) > 32:
                job_name = job_name[0:32]

        jt.jobName = job_name

        # Send job to cluster
        job_id = self.session.runJob(jt)

        # Remove job template
        self.session.deleteJobTemplate(jt)

        return job_id

    def submit_jobs(self):
        while self.running:
            try:
                job = self.submit_queue.get(block=True, timeout=2)

                # Get job command and write to file
                command = [sys.executable,
                           os.path.join(fastr.config.executionscript),
                           job.commandfile]
                fastr.log.debug('Command to queue: {}'.format(command))

                # Make sure we do not submit after it stopped running
                if not self.running:
                    break

                fastr.log.debug('Queueing {} [{}] via DRMAA'.format(job.id, job.status))

                # Submit command to scheduler
                cl_job_id = self.send_job(command[0], command[1:],
                                          job_name='fastr_{}'.format(job.id),
                                          memory=job.required_memory,
                                          ncores=job.required_cores,
                                          walltime=job.required_time,
                                          outputLog=job.stdoutfile,
                                          errorLog=job.stderrfile,
                                          hold_job=[self.job_lookup_table[x] for x in job.hold_jobs if x in self.job_lookup_table],
                                          hold=job.status == JobState.hold,
                                          )

                # Register job in the translation tables
                self.job_translation_table[cl_job_id] = job
                fastr.log.debug('Inserting {} in lookup table pointing to {}'.format(job.id, cl_job_id))
                self.job_lookup_table[job.id] = cl_job_id
                fastr.log.info('Job {} queued via DRMAA'.format(job.id))

                # Set the queue lock to indicate there is content in the queue
                if not self.queue_lock.is_set():
                    fastr.log.debug('Setting queue_lock')
                    self.queue_lock.set()
            except Queue.Empty:
                pass

        fastr.log.info('DRMAA submission thread ended!')

    def collect_jobs(self):
        first_wait = True
        second_wait = True

        while self.running:
            # Wait for the queue to contain
            if first_wait and not self.queue_lock.is_set():
                fastr.log.debug('Waiting jobs to be queued...')

            if not self.queue_lock.wait(2):
                first_wait = False
                continue

            first_wait = True

            if second_wait:
                fastr.log.debug('Waiting for a job to finish...')

            try:
                info = self.session.wait(drmaa.Session.JOB_IDS_SESSION_ANY, 5)
                second_wait = True
            except drmaa.ExitTimeoutException:
                second_wait = False
                continue
            except drmaa.InvalidJobException:
                fastr.log.debug('No valid jobs (session queue appears to be empty)')
                fastr.log.debug('Clearing queue_lock')
                self.queue_lock.clear()
                continue
            except drmaa.NoActiveSessionException:
                if not self.running:
                    fastr.log.debug('DRMAA session no longer active, quiting collector...')
                else:
                    fastr.log.critical('DRMAA session no longer active, but DRMAA executor not stopped properly! Quitting')
                    self.running = False
                continue
            except drmaa.errors.DrmaaException as exception:
                # Avoid the collector getting completely killed on another DRMAA exception
                fastr.log.warning('Encountered unexpected DRMAA exception: {}'.format(exception))
                second_wait = True
                continue
            except Exception as exception:
                if exception.message.startswith('code 24:'):
                    # Avoid the collector getting completely killed this specific exception
                    # This is generally a job that got cancelled or something similar
                    fastr.log.debug('Encountered (probably harmless) DRMAA exception: {}'.format(exception))
                    second_wait = True
                    continue
                else:
                    fastr.log.error('Encountered unexpected exception: {}'.format(exception))
                    second_wait = True
                    continue

            fastr.log.debug('Cluster DRMAA job {} finished'.format(info.jobId))

            # Create a copy of the job that finished and remove from the translation table
            errors = []
            job = self.job_translation_table.pop(info.jobId, None)

            if info.hasSignal:
                errors.append(exceptions.FastrError('Job exited because of a signal, this might mean it got killed because it attempted to use too much memory (or other resources)').excerpt())

            if job is not None:
                # Send the result to the callback function
                try:
                    del self.job_lookup_table[job.id]
                except KeyError:
                    fastr.log.warning('Found an inconsistency in the job_lookup_table, cannot find job to remove')
                self.job_finished(job, errors=errors)
            else:
                fastr.log.warning('Job {} no longer available (got cancelled?)'.format(info.jobId))

        fastr.log.info('DRMAA collection thread ended!')
