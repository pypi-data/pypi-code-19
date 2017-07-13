"""Interact with Secret Service"""

# Copyright 2016-2017 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sml.client
import sml.config


class SecretService(sml.client.SherlockMLService):
    """A Secret Service client"""

    def __init__(self):
        super(SecretService, self).__init__(sml.config.secret_service_url())

    def db_details(self, project_id):
        """Get database details for the given project"""
        resp = self._get('/database/{}'.format(project_id))
        return resp.json()
