import re
import requests
requests.packages.urllib3.disable_warnings()

__all__ = ['TaliaBeeAPIError', 'TaliaBeeIO']


class TaliaBeeAPIError(Exception):
    pass


class TaliaBeeIO(object):
    COMPONENT_GET_PATTERN = re.compile('^([adr]o|[ad]i)([0-9]{1,2})$')
    COMPONENT_SET_PATTERN = re.compile('^([adr]o)([0-9]{1,2})$')

    def __init__(self, url='http://127.0.0.1', timeout=10, verify=False):
        super(TaliaBeeIO, self).__init__()
        self.url = url
        self.timeout = timeout
        self.verify = verify

    def __getattribute__(self, attr):
        if attr in ('COMPONENT_GET_PATTERN', 'COMPONENT_SET_PATTERN'):
            return super(TaliaBeeIO, self).__getattribute__(attr)
        matchobj = self.COMPONENT_GET_PATTERN.match(attr)
        if not matchobj:
            return super(TaliaBeeIO, self).__getattribute__(attr)
        groups = matchobj.groups()
        if groups[0] == 'di':
            return self.di_read(groups[1])

        elif groups[0] == 'do':
            return self.do_read(groups[1])

        elif groups[0] == 'ro':
            return self.ro_read(groups[1])

        elif groups[0] == 'ai':
            return self.ai_read(groups[1])

        elif groups[0] == 'ao':
            return self.ao_read(groups[1])

    def __setattr__(self, attr, val):
        matchobj = self.COMPONENT_SET_PATTERN.match(attr)
        if not matchobj:
            return super(TaliaBeeIO, self).__setattr__(attr, val)
        groups = matchobj.groups()
        if groups[0] == 'do':
            return self.do_write(groups[1], val)

        elif groups[0] == 'ro':
            return self.ro_write(groups[1], val)

        elif groups[0] == 'ao':
            return self.ao_write(groups[1], val)

    def _call(self, url):
        r = requests.get(url, timeout=self.timeout, verify=self.verify)
        if r.status_code != 200:
            raise Exception('Cannot connect. {}'.format(r.status_code))
        response = r.json()
        if response['status'] == 'ERROR':
            raise TaliaBeeAPIError(response['message'])
        return response['value']

    def di_read(self, pin):
        pin = int(pin)
        url = self.url + '/api/di/{}/read'.format(pin)
        return self._call(url)

    def do_read(self, pin):
        pin = int(pin)
        url = self.url + '/api/do/{}/read'.format(pin)
        return self._call(url)

    def do_write(self, pin, val):
        pin = int(pin)
        val = int(val)
        url = self.url + '/api/do/{}/write?val={}'.format(pin, val)
        self._call(url)

    def do_set(self, pin):
        pin = int(pin)
        url = self.url + '/api/do/{}/set'.format(pin)
        self._call(url)

    def do_reset(self, pin):
        pin = int(pin)
        url = self.url + '/api/do/{}/reset'.format(pin)
        self._call(url)

    def ro_read(self, pin):
        pin = int(pin)
        url = self.url + '/api/ro/{}/read'.format(pin)
        return self._call(url)

    def ro_write(self, pin, val):
        pin = int(pin)
        val = int(val)
        url = self.url + '/api/ro/{}/write?val={}'.format(pin, val)
        self._call(url)

    def ro_set(self, pin):
        pin = int(pin)
        url = self.url + '/api/ro/{}/set'.format(pin)
        self._call(url)

    def ro_reset(self, pin):
        pin = int(pin)
        url = self.url + '/api/ro/{}/reset'.format(pin)
        self._call(url)

    def ai_read(self, pin):
        pin = int(pin)
        url = self.url + '/api/ai/{}/read'.format(pin)
        return self._call(url)

    def ao_read(self, pin):
        pin = int(pin)
        url = self.url + '/api/ao/{}/read'.format(pin)
        return self._call(url)

    def ao_write(self, pin, val):
        pin = int(pin)
        val = int(val)
        url = self.url + '/api/ao/{}/write?val={}'.format(pin, val)
        self._call(url)

    @property
    def temperature(self):
        url = self.url + '/api/temperature/read'
        return self._call(url)

    @temperature.setter
    def temperature(self):
        raise TaliaBeeAPIError('Temperature property can not be set.')

    @property
    def status(self):
        url = self.url + '/api/status'
        return self._call(url)

    def reset(self):
        url = self.url + '/api/reset'
        self._call(url)
