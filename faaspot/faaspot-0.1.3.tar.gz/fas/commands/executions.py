import json
import logging

from ..utils import WaitCompletion
from .command import Command

logger = logging.getLogger(__name__)


class Executions(Command):
    def __init__(self, *args, **kwargs):
        super(Executions, self).__init__(*args, **kwargs)

    def list(self, include_completed=False, deployment=None):
        self.columns = ['name', 'status', 'output', 'uuid', 'created']
        logger.debug('Going to retrieve all execution. include completed: `{0}`'.format(all))
        uri = 'executions/'
        executions = self.api.get(uri=uri,
                                  params={'deployment': deployment,
                                          'include_completed': include_completed})
        return executions

    @WaitCompletion(logger=logger)
    def get(self, uuid, **kwargs):
        if isinstance(uuid, list):
            raise Exception('Expecting one UUID string. Use get_bulk for multiple UUID request')
        logger.debug('Going to retrieve status of execution: `{0}`'.format(uuid))
        uri = 'executions/{0}'.format(uuid)
        execution = self.api.get(uri=uri)
        return execution

    def get_bulk(self, uuid, **kwargs):
        if not isinstance(uuid, list) or len(uuid) == 0:
            raise Exception('Expecting list of Executions UUID')
        # the cli pass list of lists..
        uuid_list = [item[0] for item in uuid] if isinstance(uuid[0], list) else uuid
        logger.debug('Going to retrieve bulk status of executions: `{0}`'.format(uuid_list))
        data = json.dumps(uuid_list)
        uri = 'executions/bulk'
        executions = self.api.post(uri=uri, data=data)
        return executions

    def cancel(self, uuid):
        logger.debug('Going to cancel execution: `{0}`'.format(uuid))
        uri = 'executions/{0}'.format(uuid)
        response = self.api.delete(uri=uri)
        return response
