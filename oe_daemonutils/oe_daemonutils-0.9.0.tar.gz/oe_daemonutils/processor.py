import transaction
import feedparser
import dateutil.parser
from redis import ConnectionError

from oe_daemonutils.circuit import DaemonCircuitBreaker
from oe_daemonutils.dossierservice import MasterdataNotFoundException


class EntryProcessor(object):
    def __init__(self, settings, logger, retrieve_system_token_command, service_cls):
        self.settings = settings
        self.logger = logger
        self.retrieve_system_token_command = retrieve_system_token_command
        self.process_uri = self._process_uri_list(settings.get('daemon.process.uri'))
        self.service_cls = service_cls

    @staticmethod
    def _process_uri_list(daemon_process_uri):
        if daemon_process_uri is not None:
            return daemon_process_uri.split()
        else:
            return []

    def process_entries(self, entries, last_entry_ts, daemon_manager):
        """
        Process the given entries and adapt the latest processed entry id

        :param entries: current feed entries to process
        :param last_entry_ts: the latest entry timestamp
        :param daemon_manager: data manager for the current daemon
        """
        service = self.service_cls(self.settings, self.logger, self.retrieve_system_token_command.execute())
        notifications_dict = {}

        for entry in entries:
            current_entry_ts = entry.updated
            process_uri = next(
                (link['href'] for link in entry.links if link['rel'] == 'related' and link['title'] == 'proces'), None)
            if not process_uri:
                self.logger.error('Entry {0} has no process!'.format(entry.id))
            else:
                self._process_entry(entry, service, notifications_dict)
            current = last_entry_ts
            last_entry_ts = current_entry_ts if current_entry_ts is not None else last_entry_ts
            with transaction.manager as manager:
                daemon_manager.update_last_entry_id(current=current, last=last_entry_ts)
                manager.commit()

        return notifications_dict

    def _process_entry(self, entry, service, notifications_dict):
        """
        Common method to create a dossier from an entry
        Keep track of the entry to notify the persons concerned

        :param entry: entry to process
        :param service: service to use for processing
        :param notifications_dict: notifications_dict
        """
        self.logger.info('Processing entry {0}'.format(entry.id))
        print('Processing entry {0}'.format(entry.id))
        try:
            entry_process_uri = next(
                (link['href'] for link in entry.links if link['rel'] == 'related' and link['title'] == 'proces'), None)
            self.logger.info('Entry Process URI {0}'.format(entry_process_uri))
            if entry_process_uri in self.process_uri:
                service.create_dossier(entry, notifications_dict)
        except MasterdataNotFoundException as e:
            self.logger.warn(e.__str__())


class FeedProcessor(object):
    def __init__(self, logger, feed_endpoint, failure_threshold, timeout_default, max_timeout, invocation_timeout,
                 retrieve_system_token_command):
        self.logger = logger
        self.feed_endpoint = feed_endpoint
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout
        self.retrieve_system_token_command = retrieve_system_token_command

    def _parse_feed(self, feed_endpoint):
        """
        Parse the feed given the feed endpoint

        :rtype : Feed object
        """

        feed = feedparser.parse(feed_endpoint,
                                request_headers={'OpenAmSSOID': self.retrieve_system_token_command.execute(),
                                                 'Accept': 'application/atom+xml'})
        summary = feed.feed.summary if 'summary' in feed.feed else ''
        if not hasattr(feed, 'status'):
            ex = feed.get('bozo_exception', {})
            self.logger.error('Unknown Error for url: ')
            self.logger.error(feed_endpoint)
            self.logger.error("{0} {1}".format(ex.__class__.__name__, repr(ex)))
            raise IOError('Unknown Error for url: {0}'.format(feed_endpoint), ex)
        elif 400 <= feed.status < 500:
            self.logger.error(feed.status)
            self.logger.error('Client Error for url: ')
            self.logger.error(feed_endpoint)
            self.logger.error(summary)
            raise IOError('Client Error for url: {0}'.format(feed_endpoint))
        elif 500 <= feed.status < 600:
            self.logger.error(feed.status)
            self.logger.error('Server Error for url: ')
            self.logger.error(feed_endpoint)
            self.logger.error(summary)
            raise IOError('Server Error for url: {0}'.format(feed_endpoint))
        else:
            return feed

    def _process_previous_feed(self, feed, last_entry_ts):
        """
        Check if the entries of the previous feed must be processed

        :param feed: current feed
        :param last_entry_ts: last processed entry id
        :return:
        """
        entries = []
        if hasattr(feed.feed, 'links'):
            previous_endpoint = next((link['href'] for link in feed.feed.links if link['rel'] == 'prev-archive'), None)
            if previous_endpoint:
                circuit = DaemonCircuitBreaker(self._parse_feed, self.logger, (IOError, ValueError),
                                               failure_threshold=self.failure_threshold,
                                               timeout_default=self.timeout_default,
                                               max_timeout=self.max_timeout,
                                               invocation_timeout=self.invocation_timeout)
                previous_feed = circuit.call(previous_endpoint)
                entries = self._process_feed_entries(previous_feed, last_entry_ts)
        return entries

    def _process_feed_entries(self, feed, last_entry_ts):
        """
        Get the entries of the current that are not yet processed

        :param feed: current feed
        :param last_entry_ts: last processed entry id
        :return:
        """
        entries = []
        first_ts = self.date_from_string(feed.entries[0].updated) if len(feed.entries) > 0 else None
        if first_ts is None:
            entries.extend(self._process_previous_feed(feed, last_entry_ts))
        elif first_ts and last_entry_ts is None:
            previous_endpoint = next((link['href'] for link in feed.feed.links if link['rel'] == 'prev-archive'), None)
            if previous_endpoint:
                entries.extend(self._process_previous_feed(feed, last_entry_ts))
                entries.extend(feed.entries)
            else:
                entries = feed.entries
        elif first_ts and first_ts <= last_entry_ts:
            entries = [entry for entry in feed.entries if self.date_from_string(entry.updated) > last_entry_ts]
        elif first_ts and first_ts > last_entry_ts:
            entries.extend(self._process_previous_feed(feed, last_entry_ts))
            entries.extend(feed.entries)
        return entries

    def process_feed(self, last_entry_ts_datetime):
        """
        process the feed and return the entries
        
        :param last_entry_ts_datetime: last entry timestamp in datetime format
        :return: entries_to_process: list of entries to process
        """
        entries_to_process = []

        circuit = DaemonCircuitBreaker(self._parse_feed, self.logger, (IOError, ValueError, ConnectionError),
                                       failure_threshold=self.failure_threshold,
                                       timeout_default=self.timeout_default,
                                       max_timeout=self.max_timeout,
                                       invocation_timeout=self.invocation_timeout)
        feed = circuit.call(self.feed_endpoint)

        if feed:
            entries_to_process = self._process_feed_entries(feed, last_entry_ts_datetime)

        self.logger.debug('found {0} entries to process'.format(len(entries_to_process)))
        return entries_to_process

    @staticmethod
    def date_from_string(s):
        d = dateutil.parser.parse(s) if s else None
        return d
