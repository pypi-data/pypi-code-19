"""
Manager for the :class:`bgcluster.jobs.Job`
used by web applications
"""


import os
import time
import json
import shutil
import binascii

from collections import defaultdict
from datetime import datetime
from bgcluster.jobs import DetachedJob, RemoteJob, LocalJob, Job

from bgweb.bgmanager.constants import METADATA_EXAMPLE_ID_STR, METADATA_PUBLIC_ID_STR, METADATA_USER_ID_STR, \
    METADATA_SHARED_WITH_STR, ANONYMOUS_EXPIRE_TIME, ANONYMOUS_PREFIX


class JobManagerError(Exception):
    """
    Base class for exceptions produced by the :class:`JobsManager`

    Args:
        message(str): error message

    """
    def __init__(self, message):
        self.message = message


class JobNotFoundError(JobManagerError):
    """
    Exception for not found jobs

    Args:
        job_id (str): job ID

    """

    def __init__(self, job_id):
        self.message = 'Job {} not found'.format(job_id)


class AuthorizationError(JobManagerError):
    """
    Manager exception when trying ot access a job without
    the right permissions
    """

    def __init__(self, required_level):
        self.level = required_level
        self.message = 'Authorization error'


class MaxStoredJobsError(JobManagerError):
    """
    Exception for limiting the max number of jobs each user can store

    """

    def __init__(self):
        self.message = 'You have reached the maximun number of jobs that can be stored per user. Please, delete one to leave room for a new one'


class MaxConcurrentJobsError(JobManagerError):
    """
    Exception for limiting the max number of jobs each user can store

    """

    def __init__(self):
        self.message = 'You have reached the maximun number of concurrent jobs that can be stored per user. Please, wait untill the previous jobs have finished'



class BGJobsManager:
    """
    Base class for dealing with the Jobs

    Args:
        configuration (dict): configuration for the scheduler.
          Keys: workspace, scheduler and/or scheduler_url, tee_url (optional), web_server
    """

    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def _generate_job_id():
        """
        Generate identifiers for new jobs
        """
        return binascii.hexlify(os.urandom(10)).decode('utf-8')

    def __init__(self, configuration):

        self.conf = configuration

        self.workspace = configuration['workspace']
        self.scheduler = configuration['scheduler']

        self.max_concurrent_jobs = configuration.get('concurrent_jobs', None)
        self.max_stored_jobs = configuration.get('stored_jobs', None)

        self.admins = [u.lower() for u in configuration.get('admin_users', [])]

        self.jobs = {}
        self.jobs_by_user = defaultdict(dict)
        self.example_jobs = {}

        self._load_jobs()

    def _load_jobs(self):
        # Builds a dict with all jobs in the workspace as DetachedJob
        for entry in os.scandir(self.workspace):
            if entry.is_dir():
                for folder in os.scandir(entry.path):
                    if folder.is_dir():
                        job = DetachedJob(folder.path)
                        self.jobs[folder.name] = job
                        self.jobs_by_user[entry.name][folder.name] = job
                        if job.metadata.get(METADATA_EXAMPLE_ID_STR, False):
                            self.example_jobs[folder] = job

    def _check_permissions(self, requester, job_metadata, level):

        if isinstance(requester, tuple):
            user, anonymous_user = requester
        else:
            user = requester
            anonymous_user = None

        # Admins have global access
        if user in self.admins:
            return
        elif level == 'a':
            raise AuthorizationError(level)
        # only job owners have write permissions
        elif level == 'w':
            owner = job_metadata.get(METADATA_USER_ID_STR, 'anonymous_unknown_user')
            if owner == user or owner == anonymous_user:
                return
            else:
                raise AuthorizationError('w')
        # reading permissions are given to anyone in the share list, as well as for anyone if the job is public or an example
        elif level == 'r':
            if job_metadata.get(METADATA_EXAMPLE_ID_STR, False) or job_metadata.get(METADATA_PUBLIC_ID_STR, False):  # examples and public jobs can be read by anyone
                return
            owner = job_metadata.get(METADATA_USER_ID_STR, 'anonymous_unknown_user')
            if owner == user or owner == anonymous_user:
                return
            shared = job_metadata.get(METADATA_SHARED_WITH_STR, [])
            if user in shared:
                return
        raise AuthorizationError(level)

    def _get_output_folder(self, job_metadata):
        """
        Get the directory where to store a job

        Args:
            job_metadata (dict):

        Returns:
            str. Path to the directory where to save the job

        """
        return os.path.join(self.workspace, job_metadata[METADATA_USER_ID_STR], job_metadata['id'])

    def _get_output_dir(self, job_metadata):
        """
        Get the user directory

        Args:
            job_metadata (dict):

        Returns:
            str. Path to the user directory in the workspace

        """
        return os.path.join(self.workspace, job_metadata[METADATA_USER_ID_STR])

    def _check_max_stored_jobs(self, user):
        if user not in self.admins and self.max_stored_jobs is not None:
            current_amount_of_jobs = len(self.get_user_jobs(user))
            if current_amount_of_jobs >= self.max_stored_jobs:
                raise MaxStoredJobsError()

    def _check_max_concurrent_jobs(self, user):
        if user not in self.admins and self.max_concurrent_jobs is not None:
            user_jobs = self.get_user_jobs(user)
            running_jobs = 0
            for id, job in user_jobs.items():
                if job.status == Job.WAITING or job.status == Job.RUNNING:
                    running_jobs += 1
            if running_jobs >= self.max_concurrent_jobs:
                raise MaxConcurrentJobsError()



    def get_examples(self):
        """
        Returns:
            dict. Jobs marked as examples

        """
        return self.example_jobs

    def get_jobs(self, requester):
        """

        Args:
            requester (str or tuple): user making the query

        Returns:
            dict. All jobs

        .. note::

           This method should be restricted only to admins

        """
        self._check_permissions(requester, None, 'a')
        return self.jobs

    def get_user_jobs(self, requester):
        """
        Get user jobs

        Args:
            requester (str or tuple): user making the query

        Returns:
            dict. Job for which user is owner

        """
        if isinstance(requester, tuple):
            return self.jobs_by_user.get(requester[0], {}), self.jobs_by_user.get(requester[1], {})
        else:
            return self.jobs_by_user.get(requester, {})

    def _load_job(self, job_id):
        """
        Returns a job by its id

        Args:
            job_id (str): job identifier

        Returns:
            :class:`bgcluster.jobs.Job`. A job

        Raises:
            JobNotFoundError.

        """
        try:
            return self.jobs[job_id]
        except KeyError:
            raise JobNotFoundError(job_id)

    def get_job(self, requester, job_id):
        """
        Returns a job.

        Args:
            requester (str or tuple): user making the query
            job_id (str): job ID

        Returns:
            :class:`bgcluster.jobs.Job`. A job

        """
        job = self._load_job(job_id)
        self._check_permissions(requester, job.metadata, 'r')
        return job

    def create_job(self, owner):

        self._check_max_stored_jobs(owner)

        self._check_max_concurrent_jobs(owner)

        # Create a job id
        job_id = BGJobsManager._generate_job_id()

        metadata = {'id': job_id, METADATA_USER_ID_STR: owner}

        output_folder = self._get_output_folder(metadata)
        os.makedirs(output_folder, mode=0o774)

        return metadata, output_folder

    def launch_job(self, command, metadata, scheduler=None, conda_env=None, cores=None, mask_command=None, **kwargs):
        """
        Creates a job.

        Args:
            owner (str):
            command:
            metadata:
            scheduler (str): remote or local to select the type of job. If None, it is loaded from the configuration
            conda_env:
            cores:

        Returns:
            str. Job identifier

        """
        job_id = metadata['id']
        user_id = metadata.get(METADATA_USER_ID_STR, None)
        metadata['date'] = time.strftime(BGJobsManager.TIME_FORMAT, time.localtime(time.time()))

        output_folder = self._get_output_folder(metadata)

        if scheduler is None:
            # use configuration scheduler
            scheduler = self.conf['scheduler']

        if scheduler == 'remote':
            scheduler_url = self.conf['scheduler_url']

            tee_url = self.conf.get('tee_url', None)
            if tee_url is None:
                tee_url = "{}/api/status".format(scheduler_url)

            web_server_host,  web_server_port = self.conf['web_server'].split(':')

            job = RemoteJob(command, metadata,
                            workspace=output_folder,
                            scheduler_url=scheduler_url,
                            tee_url=tee_url,
                            port=web_server_port,
                            host=web_server_host,
                            job_id=job_id,
                            cores=cores,
                            conda_env=conda_env,
                            **kwargs)
        else:
            job = LocalJob(command, metadata, workspace=output_folder,
                           conda_env=conda_env, **kwargs)

        job.send_message("LOG:# " + mask_command if mask_command is not None else command)
        job.start()
        self.jobs[job_id] = job

        self.jobs_by_user[user_id][job_id] = job

        return job_id

    def remove(self, requester, job_id):
        """
        Removes a job.

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier

        """
        job = self._load_job(job_id)

        self._check_permissions(requester, job.metadata, 'w')

        output_folder = self._get_output_folder(job.metadata)
        user_dir = self._get_output_dir(job.metadata)

        if os.path.exists(output_folder):
            self.example_jobs.pop(job_id, None)
            self.jobs.pop(job_id, None)
            self.jobs_by_user[job.metadata.get(METADATA_USER_ID_STR, None)].pop(job_id, None)
            shutil.rmtree(output_folder)
            # check if the user folder is empty
            if not os.listdir(user_dir):
                shutil.rmtree(user_dir)
        else:
            raise JobManagerError('Path not found')

    def change_metadata(self, requester, job_id, field, new_value, action='replace'):
        """
        Modify job metadata.
        This method should require write permissions, which is done
        by internally calling get_job_if_owner

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier
            field (str): field identifier
            new_value: value for the field
            action (str): operation

        ==============  ==========================================
        action          meaning
        ==============  ==========================================
        replace         set the field value to the new_value
        add/remove      add/removes a value from a list
        ==============  ==========================================

        """

        job = self._load_job(job_id)

        self._check_permissions(requester, job.metadata, 'w')

        # assuming only metadata update is required

        # Reload metadata just to be up to date
        try:
            metadata_file = os.path.join(self._get_output_folder(job.metadata), "metadata.json")
            with open(metadata_file, 'rt') as fd:
                job.metadata = json.load(fd)
        except OSError as e:
            raise JobManagerError(str(e))

        if action == 'replace':
            job.metadata[field] = new_value

        elif action == 'add':
            values = job.metadata.get(field, [])
            if new_value not in values:
                values.append(new_value)
            job.metadata[field] = values

        elif action == 'remove':
            values = job.metadata.get(field, [])
            if new_value in values:
                values.remove(new_value)
            job.metadata[field] = values

        # update the metadata
        try:
            with open(metadata_file, 'wt') as fd:
                json.dump(job.metadata, fd, indent=4)
            return
        except OSError as e:
            raise JobManagerError(str(e))

    def mark_as_example(self, requester, job_id):
        """
        Put the Job in the examples list as set the examples flag

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier

        """
        self.change_metadata(requester, job_id, METADATA_EXAMPLE_ID_STR, True)  # change metadata checks permissions
        self.example_jobs[job_id] = self._load_job(job_id)

    def unmark_as_example(self, requester, job_id):
        """
        Remove a job from the examples list and unsets the examples flag

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier

        """
        self.change_metadata(requester, job_id, METADATA_EXAMPLE_ID_STR, False)  # change metadata checks permissions
        self.example_jobs.pop(job_id, None)

    def is_example(self, requester, job_id):
        job = self.get_job(requester, job_id)  # get_jos check reading permissions
        return job.metadata.get(METADATA_EXAMPLE_ID_STR, False)

    def mark_as_public(self, requester, job_id):
        """
        Give reading rights to anyone to this job

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier

        """
        self.change_metadata(requester, job_id, METADATA_PUBLIC_ID_STR, True)  # change metadata checks permissions

    def unmark_as_public(self, requester, job_id):
        """
        Revoke public access to this job

        Args:
            requester (str or tuple): user making the query
            job_id (str): job indentifier

        """
        self.change_metadata(requester, job_id, METADATA_PUBLIC_ID_STR, False)  # change metadata checks permissions

    def is_public(self, requester, job_id):
        job = self.get_job(requester, job_id)  # get_jos check reading permissions
        return job.metadata.get(METADATA_PUBLIC_ID_STR, False)

    def share_with(self, requester, job_id, user):
        self.change_metadata(requester, job_id, METADATA_SHARED_WITH_STR, user, 'add')  # change metadata checks permissions

    def unshare_with(self, requester, job_id, user):
        self.change_metadata(requester, job_id, METADATA_SHARED_WITH_STR, user, 'remove')  # change metadata checks permissions

    def is_owner(self, requester, job_id):
        """
        Check if the requester is the job owner

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier

        Returns:
            bool.

        """
        job = self.get_job(requester, job_id)
        owner = job.metadata.get(METADATA_USER_ID_STR, 'anonymous_unknown_user')
        if isinstance(requester, tuple):
            return owner in requester
        else:
            return owner == requester

    def add_handler(self, job_id, handler):
        """
        Add a handler to an specific job.
        This function does not require any permission

        Args:
            job_id (str): job ID
            handler:

        """
        job = self._load_job(job_id)
        job.add_handler(handler)

    def send_message(self, job_id, message):
        """
        Sends a message to the client.
        This method should not require any permission

        Args:
            job_id (str): job ID
            message:

        """
        job = self._load_job(job_id)
        job.send_message(message)

    @staticmethod
    def _is_anonymous(user):
        """
        Check if a user is anonymous or not

        Args:
            user (str): user identifier

        Returns:
            bool.

        """
        return user.startswith(ANONYMOUS_PREFIX) and '@' not in user

    def clean_anonymous_jobs(self):
        """
        Check for anonymous jobs that have expired and remove them
        """
        now = datetime.now()

        users = list(self.jobs_by_user.keys())

        for user in users:
            if BGJobsManager._is_anonymous(user):
                user_jobs = self.jobs_by_user[user]
                self.jobs_by_user[user] = {}

                for job_id, job in user_jobs.items():
                    date = datetime.strptime(job.metadata['date'], BGJobsManager.TIME_FORMAT)
                    remove_it = (now - date).seconds > ANONYMOUS_EXPIRE_TIME

                    if remove_it:
                        self.example_jobs.pop(job_id, None)
                        self.jobs.pop(job_id, None)
                        output_folder = self._get_output_folder(job.metadata)
                        if os.path.exists(output_folder):
                            shutil.rmtree(output_folder)
                        else:
                            continue
                    else:
                        self.jobs_by_user[user][job_id] = job

                if self.jobs_by_user[user] == {}:
                    self.jobs_by_user.pop(user, None)
                    user_dir = os.path.join(self.workspace, user)
                    # check if the user folder is empty
                    if not os.listdir(user_dir):
                        shutil.rmtree(user_dir)

    def change_owner(self, requester, job_id, new_owner):
        """
        Modify the owner of the job

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier
            new_owner (str): new owner of the job
        """
        self._check_max_stored_jobs(new_owner)

        job = self._load_job(job_id)
        current_owner = job.metadata[METADATA_USER_ID_STR]
        self.change_metadata(requester, job_id, METADATA_USER_ID_STR, new_owner)

        if current_owner is not None:
            self.jobs_by_user[new_owner][job_id] = self.jobs_by_user[current_owner].pop(job_id)
        else:
            self.jobs_by_user[new_owner][job_id] = job

        origin = os.path.join(self.workspace, current_owner)
        destination = self._get_output_dir(job.metadata)
        shutil.move(origin, destination)

    def get_directory(self, requester, job_id):
        """

        Args:
            requester (str or tuple): user making the query
            job_id (str): job identifier

        Returns:
            str. Output directory of the job

        """
        job = self.get_job(requester, job_id)  # get_job check reading permission
        return self._get_output_folder(job.metadata)


class BGBaseJobsManager(BGJobsManager):

    def _load_jobs(self):
        # Builds a dict with all jobs in the workspace as DetachedJob
        self.jobs_by_user = defaultdict(dict)
        self.example_jobs = {}
        for folder in os.listdir(self.workspace):
            job = DetachedJob(os.path.join(self.workspace, folder))
            self.jobs[folder] = job
            if job.metadata.get(METADATA_EXAMPLE_ID_STR, False):
                self.example_jobs[folder] = job
            user = job.metadata.get(METADATA_USER_ID_STR, None)
            if user is not None:
                self.jobs_by_user[user][folder] = job

    def _get_output_folder(self, job_metadata):
        """
        Computes the output folder from the job metadata

        Args:
            job_metadata (dict): job metadata

        Returns:
            str. Output folder for a job

        .. note::

           Job metadata requires field 'id'

        """
        return os.path.join(self.workspace, job_metadata['id'])

    def _get_output_dir(self, job_metadata):
        """
        Get the user directory

        Args:
            job_metadata (dict):

        Returns:
            str. Path to the user directory in the workspace

        """
        return self.workspace

    def clean_anonymous_jobs(self):
        """
        Check for anonymous jobs that have expired and remove them
        """
        now = datetime.now()

        users = list(self.jobs_by_user.keys())

        for user in users:
            if BGJobsManager._is_anonymous(user):
                user_jobs = self.jobs_by_user[user]
                self.jobs_by_user[user] = {}

                for job_id, job in user_jobs.items():
                    date = datetime.strptime(job.metadata['date'], BGJobsManager.TIME_FORMAT)
                    remove_it = (now - date).seconds > ANONYMOUS_EXPIRE_TIME

                    if remove_it:
                        self.example_jobs.pop(job_id, None)
                        self.jobs.pop(job_id, None)
                        output_folder = self._get_output_folder(job.metadata)
                        if os.path.exists(output_folder):
                            # user = job.metadata.get(METADATA_USER_ID_STR, None)
                            shutil.rmtree(output_folder)
                        else:
                            continue
                    else:
                        self.jobs_by_user[user][job_id] = job

                if self.jobs_by_user[user] == {}:
                    self.jobs_by_user.pop(user, None)

    def change_owner(self, requester, job_id, new_owner):
        """
        Change owner of a job. Useful for anonymous jobs

        Args:
            requester (str or tuple): user ID or user and anonymous user IDs
            job_id (str): job identifier
            new_owner (str): user identifier

        """
        job = self._load_job(job_id)
        current_owner = job.metadata.get(METADATA_USER_ID_STR, None)

        self.change_metadata(requester, job_id, METADATA_USER_ID_STR, new_owner)

        if current_owner is not None:
            self.jobs_by_user[new_owner][job_id] = self.jobs_by_user[current_owner].pop(job_id)
        else:
            self.jobs_by_user[new_owner][job_id] = job
