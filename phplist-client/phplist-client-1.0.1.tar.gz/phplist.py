import logging
import requests

logger = logging.getLogger(__name__)


class CommandNotFoundError(Exception):

    def __init__(self, command):
        self.command = command
        message = "Command %s not found on server" % command
        super(CommandNotFoundError, self).__init__(message)


class PHPListClient:

    def __init__(self, url, secret=None):
        self.url = url
        self.secret = secret
        self.session = requests.Session()

    def __getattr__(self, name):
        """try to automatically determine the API call"""
        if '_' in name:
            name_parts = name.split('_')
            command = ''.join([name_parts[0]] + [p.capitalize() for p in name_parts[1:]])
        else:
            command = name
        def apicall(**kwargs):
            return self.call_api(command, kwargs)
        return apicall

    def call_api(self, command, params):
        params['cmd'] = command
        if self.secret:
            params['secret'] = self.secret
        r = self.session.post(self.url, data=params)
        r.raise_for_status()
        output = r.json()
        logger.debug("output: %r", output)
        if output['status'] != 'success':
            if output['status'] == 'error':
                if output['data']['message'] == 'No function for provided [cmd] found!':
                    raise CommandNotFoundError(command)
                else:
                    raise ValueError(output['data']['message'])
            else:
                raise Exception("don't know how to handle: %r" % output)
        return output
