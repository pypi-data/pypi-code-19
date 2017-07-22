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
            return self._get_bulk(uuid)
        logger.debug('Going to retrieve status of execution: `{0}`'.format(uuid))
        uri = 'executions/{0}'.format(uuid)
        execution = self.api.get(uri=uri)
        return execution

    def cancel(self, uuid):
        logger.debug('Going to cancel execution: `{0}`'.format(uuid))
        uri = 'executions/{0}'.format(uuid)
        response = self.api.delete(uri=uri)
        return response

    def _get_bulk(self, uuid_list):
        logger.debug('Going to retrieve bulk status of {0} executions'.format(len(uuid_list)))
        data = {'tasks': json.dumps(uuid_list)}
        uri = 'executions/bulk'
        execution = self.api.post(uri=uri,
                                  data=data)
        return execution
