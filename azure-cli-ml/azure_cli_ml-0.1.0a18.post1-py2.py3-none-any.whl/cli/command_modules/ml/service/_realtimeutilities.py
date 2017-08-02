# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utilities to create and manage realtime web services.

"""

from __future__ import print_function

import os
import tarfile
import uuid
import requests
import tempfile
from collections import OrderedDict
from .._util import TraversalFunction

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    # python 2
    from urlparse import urlparse

realtime_view_service_header_to_fn_dict = OrderedDict([('Name', TraversalFunction(('Name',))),
                                                       ('Service_Id', TraversalFunction(('Id',))),
                                                       ('Image_Id', TraversalFunction(('Image', 'Id',)))])

realtime_view_service_details_header_to_fn_dict = OrderedDict([('Created_At', TraversalFunction(('CreatedAt',))),
                                                               ('Last_Updated', TraversalFunction(('UpdatedAt',))),
                                                               ('Scoring_Uri', TraversalFunction(('ScoringUri',))),
                                                               ('State', TraversalFunction(('State',)))])

realtime_list_service_header_to_fn_dict = OrderedDict([('Name', TraversalFunction(('Name',))),
                                                       ('Service_Id', TraversalFunction(('Id',))),
                                                       ('Last_Updated', TraversalFunction(('UpdatedAt',))),
                                                       ('Image_Id', TraversalFunction(('Image', 'Id',))),
                                                       ('State', TraversalFunction(('State',)))])


acs_connection_timeout = 2

def upload_dependency(context, dependency, verbose):
    """

    :param context: CommandLineInterfaceContext object
    :param dependency: path (local, http[s], or wasb[s]) to dependency
    :param verbose: bool indicating verbosity
    :return: (int, str, str): statuscode, uploaded_location, dependency_name
    status codes:
       -1: Error - path does not exist
       0: Success, dependency was already remote or uploaded to blob.
       1: Success, dependency was a directory, uploaded to blob.
    """
    if dependency.startswith('http') or dependency.startswith('wasb'):
        return 0, dependency, urlparse(dependency).path.split('/')[-1]
    if not os.path.exists(dependency):
        if verbose:
            print('Error: no such path {}'.format(dependency))
        return -1, '', ''
    elif os.path.isfile(dependency):
        az_container_name = 'amlbdpackages'
        az_blob_name = os.path.basename(dependency)
        package_location = context.upload_dependency_to_azure_blob(dependency, az_container_name, az_blob_name)
        print(' {}'.format(dependency))
        return 0, package_location, az_blob_name
    elif os.path.isdir(dependency):
        arcname = os.path.basename(dependency.strip('/'))
        if verbose:
            print('[Debug] name in archive: {}'.format(arcname))
        az_blob_name = str(uuid.uuid4()) + '.tar.gz'
        tmpdir = tempfile.mkdtemp()
        tar_name = os.path.join(tmpdir, az_blob_name)
        dependency_tar = tarfile.open(tar_name, 'w:gz')
        dependency_tar.add(dependency, arcname=arcname)
        dependency_tar.close()
        az_container_name = 'amlbdpackages'
        package_location = context.upload_dependency_to_azure_blob(tar_name, az_container_name, az_blob_name)
        print(' {}'.format(dependency))
        return 1, package_location, az_blob_name


def check_marathon_port_forwarding(context):
    """

    Check if port forwarding is set up to the ACS master
    :return: int - -1 if config error, 0 if direct cluster connection is set up, local port otherwise
    """
    return context.check_marathon_port_forwarding()


def resolve_marathon_base_url(context):
    """
    Determines the marathon endpoint of the configured ACS cluster
    :return: str - None if no marathon endpoint found, http://FQDN:[port] otherwise
    """
    marathon_base_url = None
    forwarded_port = check_marathon_port_forwarding(context)
    if forwarded_port > 0:
        marathon_base_url = 'http://127.0.0.1:' + str(forwarded_port)
    else:
        if context.acs_master_url is not None:
            cluster = context.acs_master_url
            marathon_base_url = 'http://' + cluster
        else:
            print("")
            print("No valid ACS found. Please run 'az ml env about' for instructions on setting up your environment.")
            print("")

    return marathon_base_url


def get_sample_data(swagger_url, headers=None, verbose=False):
    """
    Try to retrieve sample data for the given service.
    :param swagger_url: The url to the service's swagger definition
    :param headers: The headers to pass in the call
    :param verbose: Whether to print debugging info or not.
    :return: str - sample data if available, '' if not available, None if the service does not exist.
    """
    default_retval = None
    if verbose:
        print('[Debug] Fetching sample data from swagger endpoint: {}'.format(swagger_url))
    try:
        swagger_spec_response = requests.get(swagger_url, headers=headers, timeout=acs_connection_timeout)
    except (requests.ConnectionError, requests.exceptions.Timeout):
        if verbose:
            print('[Debug] Could not connect to sample data endpoint on this container.')
        return default_retval

    if swagger_spec_response.status_code == 404:
        if verbose:
            print('[Debug] Received a 404 - no swagger specification for this service.')
        return ''
    elif swagger_spec_response.status_code == 503:
        if verbose:
            print('[Debug] Received a 503 - no such service.')
        return default_retval
    elif swagger_spec_response.status_code != 200:
        if verbose:
            print('[Debug] Received {} - treating as no such service.'.format(swagger_spec_response.status_code))
        return default_retval

    try:
        input_swagger = swagger_spec_response.json()['definitions']['ServiceInput']
        if 'example' in input_swagger:
            sample_data = input_swagger['example']
            return str(sample_data)
        else:
            return default_retval
    except ValueError:
        if verbose:
            print('[Debug] Could not deserialize the service\'s swagger specification. Malformed json {}.'.format(
                swagger_spec_response))
        return default_retval
