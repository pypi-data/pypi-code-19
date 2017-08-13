# Copyright (c) 2017 XLAB d.o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module with job related functionality.
"""

from requests import codes

from fcoclient.resources.base import JobStatus  # noqa
from fcoclient.resources.base import BaseClient, Job


class JobClient(BaseClient):
    """
    Job client.

    This class groups all operations that can be executed on jobs.
    """

    klass = Job

    def wait(self, uuid):
        """
        Wait for job to terminate.

        Note that this function does not check if job terminated in error.
        This is responsibility of the caller.

        Args:
            uuid: Job to wait for
        """
        return self.wait_for_condition(uuid, lambda x: x.status.is_terminal)

    def delete(self, uuid, cascade=False):
        """
        Delete job.

        Job is deleted synchronously and thus needs it's own delete
        implementation.

        Args:
            uuid (str): UUID of the job being deleted.
            cascade (bool): Control whether child resources are also deleted
                or not. This parameter is ignored and set to ``False``
                unconditionally.
        """
        endpoint = "{}/{}".format(self.endpoint, uuid)
        data = {"cascade": False}
        self.client.delete(endpoint, data, codes.ok)
