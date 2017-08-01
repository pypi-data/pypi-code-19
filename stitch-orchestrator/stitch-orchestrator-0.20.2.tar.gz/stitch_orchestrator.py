#!/usr/bin/env python3

import datetime
import time
import os
import threading
import json
from subprocess import Popen, PIPE
import logging
import logging.config

import attr
import datadog
import requests
import backoff
import singer.metrics as metrics

ISO_FMT = "%Y-%m-%d %H:%M:%S"
RFC_FMT = "%Y-%m-%dT%H:%M:%SZ"

SYNC_TIMEOUT = 60 * 60 * 5.75 # 5.75 hours
CHECK_TIMEOUT =  60 * 5 # 5 minutes

SYNC_TIMEOUT_ERROR_MESSAGE = "The integration job was taking longer than expected to replicate data. It has been terminated and will resume syncing immediately where it left off."


def init_logger():
    this_dir = os.path.split(__file__)[0]
    path = os.path.join(this_dir, 'stitch_orchestrator/logging.conf')
    logging.config.fileConfig(path)
    return logging.getLogger('root')

LOGGER = init_logger()


@attr.s
class Environment(object):
    config_dir = attr.ib(default=None)
    connection_service_host = attr.ib(default=None)
    connection_service_token = attr.ib(default=None)
    menagerie_service_host = attr.ib(default=None)
    tap_name = attr.ib(default=None)
    tap_version = attr.ib(default=None)
    target_name = attr.ib(default=None)
    target_version = attr.ib(default=None)
    target_dry_run = attr.ib(default=None)
    dogstatsd_host = attr.ib(default=None)
    dogstatsd_port = attr.ib(default=None)
    client_id = attr.ib(default=None)
    connection_id = attr.ib(default=None)
    tap_path = attr.ib(default=None)
    target_path = attr.ib(default=None)
    mode = attr.ib(default=None)
    job_name = attr.ib(default=None)

ENV = Environment()


def dump_json(data, filename):
    path = os.path.join(ENV.config_dir, filename)
    with open(path, 'w') as out:
        json.dump(data, out)
    return path


class MenagerieException(Exception):
    pass


class ConnectionServiceClient(object):
    """Simple client for connection service that just knows how to get a
connection given client id and connection id and decrypt the credentials."""

    def __init__(self):
        token = ENV.connection_service_token
        self.session = requests.Session()
        self.session.headers.update(
            {'Authorization': 'Bearer {}'.format(token)})

    def get_connection(self):
        url = '{}/clients/{}/connections/{}'.format(
            ENV.connection_service_host,
            ENV.client_id,
            ENV.connection_id)
        LOGGER.debug('Getting connection from %s', url)
        response = request(self.session, method='get', url=url)
        if response.json() is None:
            raise Exception("Empty connection response")
        return response.json()


# Utility functions for getting fields from connection
def get_token(connection):
    if connection.get('import_token', None) is not None:
        return connection['import_token']
    elif 'credentials' in connection and 'paws_key' in connection['credentials']:
        return connection['credentials']['paws_key']
    else:
        raise Exception('paws_key required in connection.credentials')


def get_stitch_url(connection):
    if connection.get('import_url', None) is not None:
        return connection['import_url']
    elif 'paws_url' in connection['properties']:
        return connection['properties']['paws_url']


def scrub_string(string, secrets):
    """Given a string and a list of secrets, scrubs s of every secret."""
    for secret in secrets:
        if secret is not None and len(secret) > 2:
            string = string.replace(secret, '.'*len(secret))
    return string


ALLOWED_METRICS = [
    metrics.Metric.record_count,
    metrics.Metric.http_request_duration,
    metrics.Metric.job_duration,
]

ALLOWED_TAGS = [
    metrics.Tag.endpoint,
    metrics.Tag.job_type,
    metrics.Tag.http_status_code,
    metrics.Tag.status
]


def tags_for_metric(point):
    tags = ['tap:' + ENV.tap_name,
            'tap_version:' + ENV.tap_name + '-' + ENV.tap_version]

    tag_fields = [
        metrics.Tag.endpoint,
        metrics.Tag.status,
        metrics.Tag.http_status_code
    ]

    for field in tag_fields:
        val = point.tags.get(field)
        if val is not None:
            tags.append(field + ':' + str(val))

    return tags


class ProcessType:
    tap = 'tap'
    target = 'target'

# For certain timer metrics that the Taps emit, we can automatically
# create a counter metric. For example, if a Tap emits metrics for the
# duration of each HTTP request, we can create a counter for HTTP
# requests.
TIMER_METRIC_TO_COUNTER_METRIC = {
    'http_request_duration': 'http_request_count',
    'job_duration': 'job_count',
}

class StderrReader(threading.Thread):

    def __init__(self, process, proc_type, secrets):
        self.process = process
        self.proc_type = proc_type
        self.secrets = secrets
        self.last_line = None
        self.dogstatsd = get_dogstatsd()
        thread_name = proc_type + '_log'
        super().__init__(name=thread_name)

    def _publish_metric(self, line):
        point = metrics.parse(line)
        if not (point and
                point.metric in ALLOWED_METRICS and
                self.dogstatsd and
                self.proc_type == ProcessType.tap):
            return

        tags = tags_for_metric(point)
        metric = 'singer.tap.' + point.metric

        if point.metric_type == 'timer':
            self.dogstatsd.gauge(metric, point.value, tags)
            counter_metric = TIMER_METRIC_TO_COUNTER_METRIC.get(point.metric)
            if counter_metric:
                self.dogstatsd.increment('singer.tap.' + counter_metric, 1, tags)

        elif point.metric_type == 'counter':
            self.dogstatsd.increment(metric, point.value, tags=tags)

    def run(self):
        LOGGER.debug("Thread starting")
        for raw_line in self.process.stderr:
            for line in raw_line.splitlines():
                scrubbed_line = scrub_string(line, self.secrets)
                LOGGER.info(scrubbed_line)
                self._publish_metric(scrubbed_line)
                self.last_line = scrubbed_line
        LOGGER.debug("Thread terminating")

    def finish_reading_logs(self):
        """Joins the thread with a timeout.

        Intended to be called on the parent thread.
        """
        LOGGER.debug('Joining on thread %s', self.name)
        self.join(timeout=5)
        if self.is_alive():
            LOGGER.warning(
                'Thread %s did not finish within timeout', self.name)
        else:
            LOGGER.debug('Thread %s finished', self.name)


class MenagerieClient(object):
    """Persists state to Menagerie"""

    def __init__(self, token):
        client_id = ENV.client_id
        connection_id = ENV.connection_id
        self.get_state_url = "{}/menagerie/public/v2/clients/{}/connections/{}/state".format( # pylint: disable=line-too-long
            ENV.menagerie_service_host,
            client_id, connection_id)
        self.put_state_url = "{}/menagerie/public/v1/clients/{}/connections/{}/state".format( # pylint: disable=line-too-long
            ENV.menagerie_service_host,
            client_id, connection_id)
        self.exit_status_url = "{}/menagerie/public/v1/clients/{}/connections/{}/exit-status".format( # pylint: disable=line-too-long
            ENV.menagerie_service_host,
            client_id, connection_id)
        self.discovered_schemas_url = "{}/menagerie/public/v1/clients/{}/connections/{}/discovered-streams".format( # pylint: disable=line-too-long
            ENV.menagerie_service_host,
            client_id, connection_id)
        self.selected_properties_url = "{}/menagerie/public/v1/clients/{}/connections/{}/annotated-streams".format( # pylint: disable=line-too-long
            ENV.menagerie_service_host,
            client_id, connection_id)
        self.session = requests.Session()
        self.session.headers.update(
            {'Authorization': 'Bearer {}'.format(token)})
        self.state_version = None

    def ensure_bookmark_standard_in_state(self, old_state, connection, props):
        stream_to_bookmark_key = {'contacts' : 'lastmodifieddate', 'subscription_changes': 'startTimestamp',
                                  'forms' : 'updatedAt', 'deals': 'hs_lastmodifieddate',
                                  'workflows' : 'updatedAt', 'owners' : 'updatedAt',
                                  'keywords': 'created_at', 'email_events': 'startTimestamp',
                                  'companies' : 'hs_lastmodifieddate'}

        if connection['type'] == 'platform.hubspot':
            LOGGER.info("ensure_bookmark_standard_in_state for hubspot")
            # Taps that support the new state format need to be transformed
            new_state = {'bookmarks': {}}
            supported_bookmarks = [stream['tap_stream_id'] for stream in props['streams']]
            for k,v in old_state.items():
                if k in {'campaigns', 'contact_lists', 'this_stream'}:
                    continue
                if k in supported_bookmarks:
                    new_state['bookmarks'][k] = { stream_to_bookmark_key.get(k) : v}
                else:
                    new_state[k] = v

            LOGGER.info(new_state)
            return new_state
        else:
            return old_state

    def load_state(self, connection, props):
        LOGGER.debug('Getting initial state from %s', self.get_state_url)
        response = request(self.session, method='get', url=self.get_state_url)

        #for hubspot, transform state
        data = response.json()
        self.state_version = data['version']

        return self.ensure_bookmark_standard_in_state(data['state'], connection, props)

    def save_state(self, state):
        LOGGER.debug('Saving state to menagerie: %s', state)
        data = {
            'state': state,
            'version': self.state_version
        }
        response = request(
            self.session, url=self.put_state_url, method='put', json=data)
        if not (response.status_code >= 200 and
                response.status_code < 300):
            raise Exception('Error saving state: %s', response)
        else:
            response_body = response.json()
            if 'error' in response_body:
                raise MenagerieException(response_body['error'])
            else:
                self.state_version = response_body['version']

    def save_exit_status(self, exit_status):
        body = {
            'tap_name': ENV.tap_name,
            'tap_version': ENV.tap_version,
            'target_name': ENV.target_name,
            'target_version': ENV.target_version,
            'tap_code': exit_status.get('tap_code'),
            'tap_description': exit_status.get('tap_description'),
            'target_code': exit_status.get('target_code'),
            'target_description': exit_status.get('target_description'),
            'discovery_code': exit_status.get('discovery_code'),
            'discovery_description': exit_status.get('discovery_description'),
            'check_code': exit_status.get('check_code'),
            'mode': ENV.mode,
            'job_name': ENV.job_name
        }
        LOGGER.debug('Full exit status is: %s', body)
        request_without_backoff(self.session,
                url=self.exit_status_url,
                method='post',
                json=body)

    def save_discovered_schemas(self, discovered_schemas):
        LOGGER.debug("Saving discovered schemas")
        request(self.session,
                url=self.discovered_schemas_url,
                method='put',
                json=discovered_schemas)

    def load_selected_properties(self):
        url = self.selected_properties_url
        LOGGER.debug('Getting selected properties from %s', url)
        response = request(self.session, method='get', url=url)
        return response.json()


class Terminator(threading.Thread):

    def __init__(self, proc, timeout):
        self.proc = proc
        self.timeout = timeout
        super().__init__(name='terminator', daemon=True)
        self.triggered = False

    def _sleep(self, seconds):
        time.sleep(seconds)

    def run(self):
        LOGGER.debug('Giving subprocess %.2f seconds to complete', self.timeout)
        self._sleep(self.timeout)
        LOGGER.error('Time limit hit. Terminating subprocesses.')
        self.triggered = True
        self.proc.terminate()


def client_error(exc):
    """Used to indicate we should give up on HTTP request"""
    return exc.response is not None and 400 <= exc.response.status_code < 500


@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=client_error,
                      factor=2)
def request(session, **kwargs):
    """Wrapper arround requests.request that uses backoff on 5xx response"""
    response = session.request(**kwargs)
    response.raise_for_status()
    return response

def request_without_backoff(session, **kwargs):
    """Wrapper arround requests.request"""
    response = session.request(**kwargs)
    response.raise_for_status()
    return response


def _parse_datetime(dtm):
    if " " in dtm:
        fmt = ISO_FMT
    else:
        fmt = RFC_FMT

    return datetime.datetime.strptime(dtm, fmt)


def _get_config(connection):
    key_values = {'user_agent': "Stitch Tap (+support@stitchdata.com)"}
    key_values.update(connection['properties'])
    key_values.update(connection['credentials'])

    if 'start_date' in key_values:
        key_values['start_date'] = _parse_datetime(key_values['start_date']).strftime(RFC_FMT)

    return key_values


def build_discover_command(connection):
    config = _get_config(connection)
    return [ENV.tap_path,
            '--config', dump_json(config, 'tap_discover_config.json'),
            '--discover']


def supports_property_selection(connection):
    return connection.get('integration', dict()).get('supports_property_selection')


def build_tap_command(connection, menagerie):
    config = _get_config(connection)
    props = None

    # Base command
    cmd = [ENV.tap_path,
           '--config', dump_json(config, 'tap_config.json')]

    # Add properties argument if needed

    if supports_property_selection(connection):
        LOGGER.info("Getting list of selected properties")
        props = menagerie.load_selected_properties()
        if props is not None:
            cmd += ['--properties', dump_json(props, 'properties.json')]

   # Add state argument if there's state
    state = menagerie.load_state(connection, props)
    if state is not None:
        cmd += ['--state', dump_json(state, 'tap_state.json')]

    return cmd


def build_target_command(connection):
    config = {
        'token': get_token(connection),
        'client_id': ENV.client_id,
        'disable_collection': True
    }

    if get_stitch_url(connection) is not None:
        config['stitch_url'] = get_stitch_url(connection)

    if ENV.target_dry_run:
        return [ENV.target_path, '--dry-run']
    else:
        return [ENV.target_path,
                '--config', dump_json(config, 'target_config.json')]


def run_discovery(command, menagerie, secrets, timeout):

    LOGGER.info('Starting tap in discovery mode: %s', " ".join(command))
    tap = Popen(command, stdout=PIPE, stderr=PIPE, bufsize=1,
                universal_newlines=True)
    tap_stderr = None
    lines = ''

    with tap:
        tap_stderr = StderrReader(tap, ProcessType.tap, secrets)
        tap_stderr.start()

        # Start thread that will terminate processes if they haven't
        # exited after a time limit
        terminator = Terminator(tap, timeout)
        terminator.start()

        for line in tap.stdout:
            lines += line

        # When we get to here, the tap.stdout has closed so we know the
        # Tap has terminated
        tap_stderr.finish_reading_logs()

    LOGGER.info('Tap exited with status %d', tap.returncode)

    if tap.returncode == 0:
        schemas = json.loads(lines)
        menagerie.save_discovered_schemas(schemas)

    return {
        'discovery_code': tap.returncode,
        'discovery_description': error_message(tap, tap_stderr, terminator.triggered)
    }


def error_message(proc, stderr_reader, terminated=False):
    if terminated:
        return SYNC_TIMEOUT_ERROR_MESSAGE
    if proc.returncode != 0:
        return stderr_reader.last_line
    return None


def run_child_processes(tap_command, target_command, menagerie, secrets, timeout):

    LOGGER.info('Starting tap: %s', " ".join(tap_command))
    tap = Popen(tap_command,
                stdout=PIPE,
                stderr=PIPE,
                bufsize=1,
                universal_newlines=True)

    tap_stderr = None
    target_stderr = None
    with tap:
        tap_stderr = StderrReader(tap, ProcessType.tap, secrets)
        tap_stderr.start()

        LOGGER.info('Starting target: %s', " ".join(target_command))
        target = Popen(target_command,
                       stdout=PIPE,
                       stderr=PIPE,
                       stdin=tap.stdout,
                       bufsize=1,
                       universal_newlines=True)
        with target:

            target_stderr = StderrReader(target, ProcessType.target, secrets)
            target_stderr.start()

            # Start thread that will terminate processes if they haven't
            # exited after a time limit
            terminator = Terminator(tap, timeout)
            terminator.start()

            for line in target.stdout:
                try:
                    state = json.loads(line)
                except Exception as exc:
                    raise Exception("Error parsing state line %s", line) from exc

                menagerie.save_state(state)

            tap_stderr.finish_reading_logs()

        if target.returncode == 0:
            LOGGER.info('Target exited normally with status %d', target.returncode)
        else:
            LOGGER.error(
                'Target exited abnormally with status %d', target.returncode)
            LOGGER.error('Terminating Tap.')
            tap.terminate()

        target_stderr.finish_reading_logs()

    return {
        'tap_code': tap.returncode,
        'tap_description': error_message(tap, tap_stderr, terminator.triggered),
        'target_code': target.returncode,
        'target_description': error_message(target, target_stderr)
    }



def get_dogstatsd():

    has_tap = ENV.tap_name and ENV.tap_version
    has_dogstatsd = ENV.dogstatsd_host and ENV.dogstatsd_port
    if has_tap and has_dogstatsd:
        constant_tags = ['tap:' + ENV.tap_name,
                         'tap_version:' + ENV.tap_name + '-' + ENV.tap_version]
        return datadog.dogstatsd.DogStatsd(
            host=ENV.dogstatsd_host,
            port=ENV.dogstatsd_port,
            constant_tags=constant_tags)
    return None


def report_to_dogstatsd(exit_status):

    dogstatsd = get_dogstatsd()

    if dogstatsd:
        succeeded = True
        for k in  ['tap_code', 'target_code', 'discovery_code']:
            if exit_status.get(k, 0) != 0:
                succeeded = False
        if succeeded:
            metric = 'orchestrator.jobs.succeeded'
        else:
            metric = 'orchestrator.jobs.failed'
        dogstatsd.increment(metric)

    else:
        LOGGER.warning('Not publishing to datadog because some ' +
                       'environment variables are not configured')

def report_check_to_dogstatsd(exit_status):

    dogstatsd = get_dogstatsd()
    if dogstatsd:
        if exit_status.get('check_code') == 0:
            metric = 'orchestrator.checks.succeeded'
        else:
            metric = 'orchestrator.checks.failed'
        dogstatsd.increment(metric)

    else:
        LOGGER.warning('Not publishing to datadog because some ' +
                       'environment variables are not configured')

def do_check(connection, secrets, menagerie):
    check_exit_status = {}
    end_time = time.time() + CHECK_TIMEOUT

    timeout = end_time - time.time()
    if supports_property_selection(connection):
        discover_command = build_discover_command(connection)
        check_exit_status.update(run_discovery(discover_command, menagerie, secrets, timeout))

    timeout = end_time - time.time()
    if  check_exit_status.get('discovery_code') == 0 or not supports_property_selection(connection):
        tap_command = build_check_tap_command(connection, ENV.config_dir)
        check_exit_status.update(run_check_child_processes(tap_command, secrets, timeout))

    return check_exit_status

def build_check_tap_command(connection, config_dir):
    config_path = os.path.join(config_dir, 'tap_config.json')

    config = _get_config(connection)
    # Write config to disk for tap
    with open(config_path, 'w') as out:
        json.dump(config, out)

   # Base command
    cmd = [ENV.tap_path, '--config', config_path]
    return cmd

def run_check_child_processes(tap_command, secrets, timeout):

    LOGGER.info("Starting tap: %s", " ".join(tap_command))
    tap = Popen(tap_command,
                stdout=PIPE,
                stderr=PIPE,
                bufsize=1,
                universal_newlines=True)

    tap_stderr = None

    record_found = False
    check_code = -1
    tap_code = None

    with tap:
        tap_stderr = StderrReader(tap, 'tap', secrets)
        tap_stderr.start()

        terminator = Terminator(tap, timeout)
        terminator.start()

        for line in tap.stdout:
            try:
                record = json.loads(line)
                if record['type'] == 'RECORD':
                    record_found = True
                    break
            except Exception as exc:
                raise Exception("Error parsing tap output: {}".
                                format(line)) from exc
        tap.terminate()
        tap_stderr.finish_reading_logs()

    if record_found or tap.returncode == 0:
        LOGGER.info("Check succeeded")
        check_code = 0
    else:
        LOGGER.info("Check failed")
        tap_code = tap.returncode

    return {
        'check_code':      check_code,
        'tap_code':        tap_code,
        'tap_description': error_message(tap, tap_stderr, terminator.triggered)
    }

def do_sync(connection, secrets, menagerie):
    exit_status = {}

    end_time = time.time() + SYNC_TIMEOUT
    if supports_property_selection(connection):
        discover_command = build_discover_command(connection)
        exit_status.update(run_discovery(discover_command, menagerie, secrets, end_time - time.time()))

    if  exit_status.get('discovery_code') == 0 or not supports_property_selection(connection):
        tap_command = build_tap_command(connection, menagerie)
        target_command = build_target_command(connection)
        exit_status.update(run_child_processes(tap_command, target_command, menagerie, secrets, end_time - time.time()))

    return exit_status

def main():
    ENV.client_id = int(os.environ['STITCH_CLIENT_ID'])
    ENV.config_dir = os.environ['STITCH_CONFIG_DIR']
    ENV.connection_id = int(os.environ['STITCH_CONNECTION_ID'])
    ENV.connection_service_host = os.environ['STITCH_CONNECTION_SERVICE_HOST']
    ENV.connection_service_token = os.environ['STITCH_CONNECTION_SERVICE_TOKEN']
    ENV.dogstatsd_host = os.environ['STITCH_DOGSTATSD_HOST']
    ENV.dogstatsd_port = os.environ['STITCH_DOGSTATSD_PORT']
    ENV.menagerie_service_host = os.environ['STITCH_MENAGERIE_SERVICE_HOST']
    ENV.tap_name = os.environ['STITCH_TAP_NAME']
    ENV.tap_path = os.environ['STITCH_TAP_PATH']
    ENV.tap_version = os.environ['STITCH_TAP_VERSION']
    ENV.target_name = os.environ['STITCH_TARGET_NAME']
    ENV.target_path = os.environ['STITCH_TARGET_PATH']
    ENV.target_version = os.environ['STITCH_TARGET_VERSION']
    ENV.target_dry_run = os.environ.get('STITCH_TARGET_DRY_RUN') or False
    ENV.mode = os.environ.get('STITCH_EXECUTION_MODE') or 'sync'
    ENV.job_name = os.environ.get('STITCH_JOB_NAME')


    connection = ConnectionServiceClient().get_connection()
    secrets = connection.get('credentials', {}).values()
    menagerie = MenagerieClient(get_token(connection))

    exit_status = None

    if ENV.mode == 'check':
        exit_status = do_check(connection, secrets, menagerie)
        report_check_to_dogstatsd(exit_status)
    else:
        exit_status = do_sync(connection, secrets, menagerie)
        report_to_dogstatsd(exit_status)

    menagerie.save_exit_status(exit_status)

if __name__ == '__main__':
    main()
