import sys
import time
import logging

from retrying import retry
from past.builtins import basestring

utils_logger = logging.getLogger(__name__)


class WaitCompletion:
    def __init__(self, logger=None):
        self._logger = logger if logger else utils_logger
        self._end_states = ['success', 'failure', 'completed', 'failed', 'cancelled']
        self._get_executions = None

    def get_executions(self, api):
        if not self._get_executions:
            # late import to avoid circular imports
            from .commands.executions import Executions
            self._get_executions = Executions()
            self._get_executions.api = api
        return self._get_executions

    def get_executions_status(self, api, task_id):
        return self.get_executions(api).get(task_id, wait=False)

    def _extract_uuid(self, response):
        if isinstance(response, basestring):
            result_arr = response.split(':')
            if len(result_arr) != 2:
                raise Exception('Expected: `Execution id: XXX`, '
                                'Got: {0}'.format(result_arr))
            return result_arr[1].strip()
        elif isinstance(response, dict) and 'uuid' in response:
            return response.get('uuid')
        raise Exception('Bad response format, Got: {0}'.format(response))

    def __call__(self, func):
        def _wait(func_self, *args, **kwargs):
            func_name = func.__name__
            wait = kwargs.get('wait', False)
            timeout = int(kwargs.get('timeout_ms', 600 * 1000))
            interval = int(kwargs.get('interval_ms', 3 * 1000))
            self._logger.debug('Running: {0}'.format(func_name))
            result = func(func_self, *args, **kwargs)
            if not wait:
                return result
            task_id = self._extract_uuid(result)
            self._logger.info('Waiting for completion of task: `{0}`'.format(task_id))
            start_time = time.time()
            try:
                response = self.verify_completion(timeout, interval, func_self, func_name, task_id)
            except AssertionError:
                elapsed_time = self._elapsed_time(start_time)
                error_message = 'Timeout waiting for {0} completion. Elapsed time: {1}'.\
                    format(func_name, elapsed_time)
                self._logger.warning(error_message)
                raise Exception(error_message)
            self._logger.info('run time: {0}'.format(self._elapsed_time(start_time)))
            return response['response']
        return _wait

    def verify_completion(self, timeout, interval, *argc, **kwargs):
        @retry(stop_max_delay=timeout, wait_fixed=interval)
        def _verify_completion(self, func_self, func_name, task_id):
            sys.stdout.write('.')
            sys.stdout.flush()
            response = self.get_executions_status(func_self.api, task_id)
            self._logger.debug('`{0}` wait for completion. '
                               'Current status: {1}'.format(func_name, response))
            status = response.get('status')
            assert status.lower() in self._end_states
            sys.stdout.write('\n')
            sys.stdout.flush()
            return {'response': response.get('output')}
        return _verify_completion(self, *argc, **kwargs)

    @staticmethod
    def _elapsed_time(start_time):
        elapsed_time_sec = int(time.time() - start_time)
        minutes, seconds = divmod(elapsed_time_sec, 60)
        return '{0}:{1}'.format(minutes, seconds)


class SafeRun:
    def __init__(self, default=None, message=None):
        self._default = default
        self._message = message

    def __call__(self, call):
        def _safeRun(*args, **kwargs):
            try:
                return call(*args, **kwargs)
            except:
                if self._message is not None:
                    try:
                        logging.exception(self._message)
                    except:
                        pass
                return self._default

        return _safeRun


# def error_handled(use_status=False, log=True):
#     def _decorator(f):
#         @wraps(f)
#         def _wrapper(*args, **kwargs):
#             try:
#                 return f(*args, **kwargs)
#             except Exception as e:
#                 if log:
#                     if 'logger' in kwargs:
#                         logger = kwargs['logger']
#                     else:
#                         logger = logging.getLogger(f.__name__)
#                     logger.exception('Exception in {0}(*{1}, **{2})'
#                                      .format(f.__name__, args, kwargs))
#                 raise
#
#         return _wrapper
#
#     return _decorator
