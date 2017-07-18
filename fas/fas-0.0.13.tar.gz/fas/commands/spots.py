import logging

from ..utils import WaitCompletion
from .command import Command
logger = logging.getLogger(__name__)


class Spots(Command):
    def __init__(self, *args, **kwargs):
        self._logger = logger
        super(Spots, self).__init__(*args, **kwargs)

    def list(self):
        self.columns = ['ip', 'created']
        logger.debug('Going to list spots..')
        uri = 'spots/'
        all = self.api.get(uri=uri)
        return all

    def get(self, ip):
        uri = 'spots/{0}'.format(ip)
        response = self.api.get(uri=uri)
        return response

    @WaitCompletion(logger=logger)
    def add(self, availability_zone=None, **kwargs):
        logger.debug('Going to create a spot')
        uri = 'spots/'
        data = {'availability_zone': availability_zone} if availability_zone else None
        task_id = self.api.put(uri=uri, data=data)
        return "Execution id: {0}".format(task_id)

    @WaitCompletion(logger=logger)
    def remove(self, ip=None, **kwargs):
        logger.debug('Going to delete a spot')
        ip = ip if ip else ''
        uri = 'spots/{0}'.format(ip)
        task_id = self.api.delete(uri=uri)
        return "Execution id: {0}".format(task_id)

    def update(self, min, max):
        if min > max:
            raise Exception('Bad arguments. min should be lower than max')
        if any(not self._is_number(x) for x in [min, max]):
            raise Exception('Bad arguments. min & max should be numbers')
        logger.debug('Going to update spot workers amount: {0} - {1}'.format(min, max))
        uri = 'spots/'
        data = {'min_workers': min,
                'max_workers': max}
        response = self.api.patch(uri=uri, data=data)
        return response

    @WaitCompletion(logger=logger)
    def refresh_ip(self, ip=None, **kwargs):
        uri = 'spots/'
        data = {'refresh_ip': ip if ip else 'all'}
        task_id = self.api.patch(uri=uri, data=data)
        return "Execution id: {0}".format(task_id)

    def replace(self, ip):
        uri = 'spots/replace/{0}'.format(ip)
        result = self.api.get(uri=uri)
        return result

    @staticmethod
    def _is_number(num):
        return isinstance(num, int) or num.isdigit()
