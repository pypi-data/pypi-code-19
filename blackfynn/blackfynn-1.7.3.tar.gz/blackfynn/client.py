# -*- coding: utf-8 -*-

import requests

# blackfynn-specific
from blackfynn import settings
from blackfynn.models import Dataset
from blackfynn.api.transfers import IOAPI
from blackfynn.api.compute import ComputeAPI
from blackfynn.api.ledger import LedgerAPI
from blackfynn.api.timeseries import TimeSeriesAPI
from blackfynn.base import ClientSession
from blackfynn.api.core import (
    CoreAPI, SecurityAPI, OrganizationsAPI, SearchAPI
)
from blackfynn.api.data import (
    DatasetsAPI, CollectionsAPI, PackagesAPI, FilesAPI, DataAPI, TabularAPI
)

def in_context(func):
    def func_wrapper(self, *args, **kwargs):
        if self.context is None:
            raise Exception('Must set context before executing method.') 
        return func(self, *args, **kwargs)
    return func_wrapper


class Blackfynn(object):
    """
    Blackfynn client for interacting with platform content
    """
    def __init__(self, 
                 email=settings.api_user,
                 password=settings.api_pass,
                 host=settings.api_host,
                 streaming_host=settings.streaming_api_host):

        if email is None:
            raise Exception("Error: empty email/user parameter. Cannot connect.")
            return
        if password is None:
            raise Exception("Error: empty password parameter. Cannot connect.")

        self.host = host
        self.streaming_host = streaming_host

        # direct interface to REST API.
        self._api = ClientSession(user=email, password=password, host=host, streaming_host=streaming_host)

        # account
        try:
            self._api.login()
        except Exception as e:
            print e
            raise Exception("Unable to login using specified user/password.")

        self._api.register(
            CoreAPI,
            OrganizationsAPI,
            DatasetsAPI,
            CollectionsAPI,
            FilesAPI,
            DataAPI,
            PackagesAPI,
            TimeSeriesAPI,
            TabularAPI,
            SecurityAPI,
            ComputeAPI,
            SearchAPI,
            IOAPI,
            LedgerAPI
        )

        # set default organization if only one present
        orgs = self.organizations()
        if len(orgs) >= 1:
            self._api._context = orgs[0]
            self._api._session.headers.update({'X-ORGANIZATION-ID': self._api._context.id})

    def set_context(self, org):
        """
        Explicitly set the organizational context for future operations.

        For example:
        >> bf = Blackfynn()
        >> bf.set_context('MyOrganization')
        >> client.datasets()

        """
        orgs_by_name = filter(lambda x: x.name.strip().lower()==org.strip().lower(), self.organizations())
        orgs_by_id   = filter(lambda x: x.id.strip()==org.strip(), self.organizations())

        orgs = orgs_by_name + orgs_by_id
        if not orgs:
            raise Exception('Unable to set context. Organization "{org}" not found.'.format(org=org))

        self._api._context = orgs[0]
        self._api._session.headers.update({'X-ORGANIZATION-ID': self._api._context.id})

    @property
    def context(self):
        return self._api._context

    @property
    def profile(self):
        """
        Returns user profile.
        """
        return self._api.profile

    def organizations(self):
        """
        Return all organizations for user.
        """
        return self._api.organizations.get_all()

    @in_context
    def datasets(self):
        """
        Return all datasets for user for an organization (current context).
        """
        return self.context.datasets

    def get(self, id, update=True):
        """
        Get any object.
        """
        return self._api.core.get(id, update=update)

    def upload(self, destination, *files):
        return self._api.io.upload_files(destination, files)

    @in_context
    def create_dataset(self, name):
        """
        Create an object on the platform. This will create the
        object and all sub-objects (if they do not exist).
        """
        return self._api.core.create(Dataset(name))

    def get_dataset(self, name_or_id):
        """
        Get Dataset by name or ID. 

        When using name, this gnores case, spaces, hyphens, and underscores
        such that these are equivelent: 

          - "My Dataset"
          - "My-dataset"
          - "mydataset"
          - "my_DataSet"
          - "mYdata SET"

        """
        result = self._api.datasets.get_by_name_or_id(name_or_id)
        if result is None:
            raise Exception("No dataset matching name or ID '{}'.".format(name_or_id))
        return result

    def update(self, thing):
        """
        Update an object on the platform.
        """ 
        return self._api.core.update(thing)

    def delete(self, *things):
        """
        Deletes objects from the platform
        """
        return self._api.core.delete(*things)

    def move(self, destination, *things):
        """
        Moves objects to the destination package
        """
        r = self._api.data.move(destination, *things)

    def search(self, query, max_results=10):
        """
        Find an object on the platform.
        """
        return self._api.search.query(query)
        
