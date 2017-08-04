"""Interact with Galleon."""

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

import dateutil.parser

import sml.client
import sml.config


class GalleonError(sml.client.SherlockMLServiceError):
    """Exception for errors interacting with Galleon."""

    pass


class Server(object):
    """A SherlockML server."""

    # pylint: disable=too-few-public-methods

    def __init__(self, id_, project_id, owner_id, name, type_, created_at,
                 status):
        self.id_ = id_
        self.project_id = project_id
        self.owner_id = owner_id
        self.name = name
        self.type_ = type_
        self.created_at = created_at
        self.status = status

    def __repr__(self):
        template = (
            'Server(id_={}, project_id={},' 'owner_id={}, name={}, '
            'type_={}, created_at={}, status={})'
        )
        return template.format(
            self.id_, self.project_id, self.owner_id,
            self.name, self.type_, self.created_at, self.status
        )

    @classmethod
    def from_json(cls, json_object):
        return cls(
            json_object['instanceId'],
            json_object['projectId'],
            json_object['ownerId'],
            json_object['name'],
            json_object['instanceType'],
            dateutil.parser.parse(json_object['createdAt']),
            json_object['status']
        )


class Galleon(sml.client.SherlockMLService):
    """A Galleon client."""

    def __init__(self):
        super(Galleon, self).__init__(sml.config.galleon_url())

    def get_all_servers(self):
        """List all SherlockML servers known to Galleon.

        This method requires administrative privileges not available to normal
        users.
        """
        resp = self._get('/instance')
        servers = [Server.from_json(o) for o in resp.json()]
        return servers

    def get_servers(self, project_id, name=None, status=None):
        """List servers in the given project."""
        params = {'name': name} if name is not None else None
        resp = self._get('/instance/{}'.format(project_id), params=params)
        servers = [Server.from_json(o) for o in resp.json()]
        if status is not None:
            servers = [s for s in servers if s.status == status]
        return servers

    def create_server(self, project_id, type_, milli_cpus, memory_mb,
                      name=None, type_version=None):
        """Create a new SherlockML server."""
        # pylint: disable=too-many-arguments
        payload = {'instanceType': type_,
                   'milliCpus': milli_cpus,
                   'memoryMb': memory_mb}
        if name:
            payload['name'] = name
        if type_version:
            payload['typeVersion'] = type_version
        resp = self._post('/instance/{}'.format(project_id), payload=payload)
        try:
            id_ = resp.json()['instanceId']
        except KeyError:
            raise GalleonError('Server created but could not retrieve ID')
        return id_

    def terminate_server(self, id_):
        """Terminate the given server."""
        return self._delete('/instance/{}'.format(id_))

    def ssh_details(self, project_id, id_):
        """Get SSH login details for the given server in the given project."""
        resp = self._get('/instance/{}/{}/ssh'.format(project_id, id_))
        return resp.json()

    def apply_environment(self, id_, environment_id):
        """Apply environment to server"""
        self._put('/instance/{}/environment/{}'.format(id_, environment_id))
