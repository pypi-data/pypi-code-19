import json
import logging
import requests

log = logging.getLogger(__name__)


class APIError(Exception):
    pass


class KnowledgeFront(object):

    """Interact with the Knowledge Front service.

    Uses the REST interface on port 443 (HTTPS) to communicate with the
    Knowledge Front monitoring service. Operations will raise APIError on
    obvious problems (such as login failure), but many errors will go
    unreported.

    """

    def __init__(self, username, password):
        """Create a KnowledgeFront object.

        Arguments:
            server   -- the address of the knowledgefront server; IP or name
            username -- the username to log in with
            password -- the password to log in with
        """

        self.username = username
        self.password = password
        self.api_url = 'https://api.knowledgefront.com/v1/'

        self.session = requests.Session()
        self.session.auth = (username, password)

        log.debug('API path is %s', self.api_url)

    def _jsondec(self, data):
        obj = json.loads(data)
        if obj['error']:
            raise APIError(obj['error'])
        else:
            return obj

    def _read(self, path, params=None):
        # Try block to handle KF being offline.
        r = self.session.get(self.api_url + path, params=params)
        r.raise_for_status()
        return self._jsondec(r.text)

    def _write(self, path, json=None):
        r = self.session.post(self.api_url + path, json=json)
        r.raise_for_status()
        return self._jsondec(r.text)

    def _update(self, path, json=None):
        r = self.session.put(self.api_url + path, json=json)
        r.raise_for_status()
        return self._jsondec(r.text)

    def _remove(self, path):
        r = self.session.delete(self.api_url + path)
        r.raise_for_status()
        return self._jsondec(r.text)

    def get_alert_status_list(self):
        """Quick summary of alert status by monitor.

        Returns a dict with the following:
            - global_alert_active boolean which is true if any alerts have been
              triggered
            - monitor_list shows alert_active per id/label

        """

        data = self._read('Status/')
        return {
            'global_alert_active': data['global_alert_active'],
            'monitor_list': data['monitor_list']
        }

    def get_monitor_list(self):
        """Retrieve all monitor configurations"""

        return self._read('Config/Monitor/')['monitor_list']

    def get_single_monitor(self, monitor):
        """Retrieve a single monitor's configuration"""

        return self._read('Config/Monitor/%s/' % monitor)['monitor']

    def create_monitor(self, label, timer, time_zone, ip_address, test_account,
                       use_tls=False, attachment=False, custom_subject=False,
                       custom_body=False, ttl=False, ipv6=False,
                       message_format=False):
        """Create a new monitor."""

        data = {
            'type': 'smtp',
            'label': label,
            'timer': timer,
            'time_zone': time_zone,
            'ip_address': ip_address,
            'test_account': test_account
        }

        if use_tls:
            data['use_tls'] = use_tls
        if attachment:
            data['attachment'] = attachment
        if custom_subject:
            data['custom_subject'] = custom_subject
        if custom_body:
            data['custom_body'] = custom_body
        if ttl:
            data['ttl'] = ttl
        if ipv6:
            data['ipv6'] = ipv6
        if message_format:
            data['message_format'] = message_format

        return self._write('Config/Monitor/', data)['monitor']

    def modify_monitor(self, monitor, label, timer, time_zone, ip_address,
                       test_account, use_tls=False, attachment=False,
                       custom_subject=False, custom_body=False):
        """Modify an existing monitor.

        Similar to Create Monitor - SMTP with the addition of an existing
        monitor id to modify in the path and changing the HTTP method to a
        PUT.

        """

        data = {
            'type': 'smtp',
            'label': label,
            'timer': timer,
            'time_zone': time_zone,
            'ip_address': ip_address,
            'test_account': test_account
        }

        if use_tls:
            data['use_tls'] = use_tls
        if attachment:
            data['attachment'] = attachment
        if custom_subject:
            data['custom_subject'] = custom_subject
        if custom_body:
            data['custom_body'] = custom_body

        return self._update('Config/Monitor/%s/' % monitor, data)['monitor']

    def delete_monitor(self, monitor):
        """Delete a monitor"""

        return self._remove('Config/Monitor/%s/' % monitor)['monitor']

    def get_alert_list(self):
        """Retrieve all alert configurations"""

        return self._read('Config/Alert/')['alert_list']

    def get_single_alert(self, alert):
        """Get a single alert's configuration"""

        return self._read('Config/Alert/%s/' % alert)['alert']

    def create_alert(self, monitor, subject_init, subject_term, timeout,
                     alert_destinations=False, message_init=False,
                     message_term=False, down_only=False, repeat=False):
        """Create a new alert"""

        data = {
            'type': 'up-down',
            'monitor': monitor,
            'subject_init': subject_init,
            'subject_term': subject_term,
            'timeout': timeout
        }

        # API bug workaround
        data['message_init'] = ""
        data['message_term'] = ""

        if alert_destinations:
            data['alert_destinations'] = alert_destinations
        if message_init:
            data['message_init'] = message_init
        if message_term:
            data['message_term'] = message_term
        if down_only:
            data['down_only'] = down_only
        if repeat:
            data['repeat'] = repeat

        return self._write('Config/Alert/', data)['alert']

    def modify_alert(self, alert, monitor, subject_init, subject_term, timeout,
                     alert_destinations=False, message_init=False,
                     message_term=False, down_only=False, repeat=False):
        """Modify an existing alert"""

        data = {
            'type': 'up-down',
            'monitor': monitor,
            'subject_init': subject_init,
            'subject_term': subject_term,
            'timeout': timeout
        }

        # API bug workaround
        data['message_init'] = ""
        data['message_term'] = ""

        if alert_destinations:
            data['alert_destinations'] = alert_destinations
        if message_init:
            data['message_init'] = message_init
        if message_term:
            data['message_term'] = message_term
        if down_only:
            data['down_only'] = down_only
        if repeat:
            data['repeat'] = repeat

        return self._update('Config/Alert/%s/' % alert, data)['alert']

    def delete_alert(self, alert):
        """Delete an existing alert from the system"""

        return self._remove('Config/Alert/%s/' % alert)['alert']

    def get_paused_alerts(self):
        """Get a list of all paused alerts and their duration"""

        return self._read('Pause/Alert/')['alert_list']

    def pause_all_alerts(self, seconds):
        """Pause all alerts for a specified timeframe"""

        # Note: This API call isn't recommended if you have a large number
        # of alerts configured (>50). It's far reaching, synchronous, and will
        # likely never return.

        data = self._write('Pause/Alert/', {'seconds': seconds})
        return {
            'alert_list': data['alert_list'],
            'seconds': data['seconds']
        }

    def pause_alerting(self, monitor, seconds):
        """Pause alerting for an individual monitor.

        If the monitor has multiple alerts, all will be paused.

        """

        # Note: This endpoint can take the id of an individual alert, instead
        # of a monitor. Although this should work in practice, it actually
        # unpauses the alert if paused, and returns as if it was successful.
        #
        # Do NOT use this with alert ids.

        data = self._write('Pause/Alert/%s/' % monitor, {'seconds': seconds})
        return {
            'alert_list': data['alert_list'],
            'seconds': data['seconds']
        }

    def enable_all_alerts(self):
        """Delete any pauses previously placed on alerts causing alerting to
        resume

        """

        # Note: This API call isn't recommended if you have a large number
        # of alerts configured (>50). It's far reaching, synchronous, and will
        # likely never return.

        return self._remove('Pause/Alert/')['alert_list']

    def enable_alerting(self, monitor):
        """Enable all alerts for a monitor"""

        return self._remove('Pause/Alert/%s/' % monitor)['alert_list']

    def get_alert_destination_list(self):
        """Retrieve a list of all Alert Destination configurations"""

        return self._read('Config/AlertDestination/')['alertdestination_list']

    def get_single_alert_destination(self, alert):
        """Get a single alert destination's configuration"""

        return self._read(
            'Config/AlertDestination/%s/' % alert)['alertdestination']

    def get_monitor_data(self, monitor, begin=False, end=False, average=False,
                         meta=False):
        """Get data for an individual monitor for a time period"""

        data = {}

        if begin:
            data['begin'] = begin
        if end:
            data['end'] = end
        if average:
            data['average'] = average
        if meta:
            data['meta'] = meta

        response = self._read('Data/Monitor/%s/' % monitor, data)
        return {key: response[key] for key in response
                if key != 'error' or key != 'path'}
