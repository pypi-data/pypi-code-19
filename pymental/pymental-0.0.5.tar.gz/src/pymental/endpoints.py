# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO

from pymental.models import Job, JobProfile, Status


class BaseEndpoint(object):

    def __init__(self, client):
        """
        :param Conductor client:
        """
        self._client = client

    @property
    def href(self):
        raise NotImplementedError

    @property
    def resource_class(self):
        raise NotImplementedError

    def get(self, identifier, params=None):
        """
        :param params: 
        :param int|str identifier:
        :rtype: self.resource_class
        :return: Resource instance
        """
        href = "{}/{}".format(self.href, identifier)
        response = self._client.get(href, params=params)

        resource = self.resource_class.parse(BytesIO(response.content))
        return resource

    def create(self, instance=None, payload=None):
        """
        :param self.resource_class instance:
        :param str payload:
        :rtype: self.resource_class
        """
        if not (instance or payload):
            raise ValueError("One of (instance, payload) is required.")

        if instance and payload:
            raise ValueError("Only one of (instance, payload) can be used.")

        xml_data = instance.unparse() if instance else payload

        response = self._client.post(self.href, data=xml_data)

        instance = self.resource_class.parse(BytesIO(response.content))
        return instance


class JobEndpoint(BaseEndpoint):
    href = '/jobs'
    resource_class = Job

    def get(self, job_id, clean=False):
        """
        :param int|str job_id:
        :param bool clean:
        :rtype: Job
        :return: Job instance
        """
        params = {'clean': clean} if clean else None
        return super(JobEndpoint, self).get(job_id, params=params)

    def create_from_profile(self, input, profile=None, payload=None, **kwargs):

        if not (profile or payload):
            raise ValueError("One of (instance, payload) is required.")

        if profile and payload:
            raise ValueError("Only one of (instance, payload) can be used.")

        profile = JobProfile.parse(payload) if payload else profile
        profile._tag = 'job'

        job = Job.parse(profile.unparse())

        job.input = input

        for k, v in kwargs.items():
            setattr(job, k, v)

        return super(JobEndpoint, self).create(instance=job)

    def status(self, resource_id):
        """

        :param int|str resource_id:
        :rtype: pymental.models.job.Status
        :return:
        """
        href = '{}/{}/status'.format(self.href, int(resource_id))
        response = self._client.get(href)
        job_status = Status.parse(BytesIO(response.content))
        return job_status


class JobProfileEndpoint(BaseEndpoint):
    href = '/job_profiles'
    resource_class = JobProfile
