# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from collections import namedtuple
from pkg_resources import resource_filename

# project


class Defaults(object):
    """
        Default values and static information
    """

    @classmethod
    def project_file(self, filename):
        return resource_filename('azurectl', filename)

    @classmethod
    def account_type_for_docopts(self, docopts, return_default=True):
        for account_type_tuple in self.__get_account_type_tuples():
            selection = account_type_tuple.command
            if selection in docopts and docopts[selection]:
                return account_type_tuple.account_type
        if return_default:
            return 'Standard_GRS'

    @classmethod
    def docopt_for_account_type(self, account_type):
        for account_type_tuple in self.__get_account_type_tuples():
            if account_type_tuple.account_type == account_type:
                return account_type_tuple.command

    @classmethod
    def max_vm_luns(self):
        """
            Maximum number of luns available on a virtual machine in
            Azure. There are 16 possible luns, numbered 0..15
        """
        return 16

    @classmethod
    def __get_account_type_tuples(self):
        """
            Maps ASM storage account_type to a backup strategy command
        """
        AccountTypeTuple = namedtuple(
            'AccountTypeTuple',
            'account_type command'
        )
        return [
            AccountTypeTuple(
                account_type='Standard_LRS',
                command='--locally-redundant'
            ),
            AccountTypeTuple(
                account_type='Standard_ZRS',
                command='--zone-redundant'
            ),
            AccountTypeTuple(
                account_type='Standard_GRS',
                command='--geo-redundant'
            ),
            AccountTypeTuple(
                account_type='Standard_RAGRS',
                command='--read-access-geo-redundant'
            )
        ]

    @classmethod
    def host_caching_for_docopts(self, docopts, return_default=True):
        for host_caching_tuple in self.__get_host_caching_tuples():
            if docopts[host_caching_tuple.command]:
                return host_caching_tuple.host_caching
        if return_default:
            return 'ReadOnly'

    @classmethod
    def __get_host_caching_tuples(self):
        """
            Maps ASM DataDisk host_caching to a caching command
        """
        HostCachingTuple = namedtuple(
            'HostCachingTuple',
            'host_caching command'
        )
        return [
            HostCachingTuple(
                host_caching='None',
                command='--no-cache'
            ),
            HostCachingTuple(
                host_caching='ReadOnly',
                command='--read-only-cache'
            ),
            HostCachingTuple(
                host_caching='ReadWrite',
                command='--read-write-cache'
            )
        ]

    @classmethod
    def get_attribute(self, instance, name):
        return getattr(instance, name)

    @classmethod
    def set_attribute(self, instance, name, value):
        return setattr(instance, name, value)

    @classmethod
    def unify_id(self, request_id):
        return format(request_id)
