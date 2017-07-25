# -*- coding: utf-8 -*-

import logging
import time
from multiprocessing import Process

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from oe_daemonutils.dossierservice.commands.security import RetrieveSystemTokenCommand
from oe_daemonutils.processor import EntryProcessor, FeedProcessor


class DaemonController(object):
    def __init__(self, settings, oauth_helper, daemon_manager_class, service_cls, notifier_class=None,
                 feed_endpoint=None, failure_threshold=5, timeout_default=60, max_timeout=300,
                 invocation_timeout=60):
        """
        Initialize the daemon feed controller given a daemon manager and a daemon processor

        :param settings: general configuration settings
        :param oauth_helper: authorization helper to get the system token
        :param daemon_manager_class: data manager class to get and update the latest feed entry id
        :param service_cls: implementation of the dossier service
        :param notifier_class: implementation of a notifier
        :param feed_endpoint: provide a custom feed endpoint (not from teh standard 'daemon.feed.endpoint' setting)
        :param failure_threshold: the couples of times the daemon should failure before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.feed_endpoint = feed_endpoint if feed_endpoint else settings['daemon.feed.endpoint']
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout
        # logging
        self.logger = logging.getLogger(settings['daemon.logger.name'])

        engine = engine_from_config(settings, 'sqlalchemy.')
        self.session_maker = sessionmaker(
            bind=engine,
            extension=ZopeTransactionExtension()
        )
        self.daemon_manager_class = daemon_manager_class
        self.notifier_class = notifier_class
        self.service_cls = service_cls
        self.settings = settings
        self.retrieve_system_token_command = RetrieveSystemTokenCommand(self.logger, oauth_helper=oauth_helper)

    def _check_entries(self):
        """
        check the feed and process new items
        """
        notifier = self.notifier_class(self.settings, self.logger) if self.notifier_class else None
        entry_processor = EntryProcessor(self.settings, self.logger, self.retrieve_system_token_command,
                                         self.service_cls)
        feed_processor = FeedProcessor(self.logger, self.feed_endpoint,
                                       self.failure_threshold,
                                       self.timeout_default,
                                       self.max_timeout,
                                       self.invocation_timeout,
                                       self.retrieve_system_token_command
                                       )
        session = self.session_maker()
        notifications_dict = None
        entries_to_process = None
        last_entry_ts = None
        last_entry_ts_datetime = None
        daemon_manager = None
        try:
            daemon_manager = self.daemon_manager_class(session)
            last_entry_ts = daemon_manager.retrieve_last_entry_id()
            last_entry_ts_datetime = feed_processor.date_from_string(last_entry_ts) if last_entry_ts else None
            entries_to_process = feed_processor.process_feed(last_entry_ts_datetime)
            notifications_dict = entry_processor.process_entries(entries_to_process, last_entry_ts, daemon_manager)

        finally:
            if notifier and notifications_dict and len(notifications_dict) > 0:
                notifier.notify(notifications_dict)
            session.close()

            del entries_to_process
            del last_entry_ts
            del last_entry_ts_datetime
            del daemon_manager
            del session
            del notifications_dict
            del notifier
            del entry_processor
            del feed_processor

    def run_daemon(self):
        """
        check the feed and process new items
        handle errors
        """

        try:
            self._check_entries()
        except Exception as ex:
            self.logger.error('error')
            self.logger.exception(ex)
            raise ex

    def _subprocess_daemon(self):
        p = Process(target=self.run_daemon, args=())
        p.start()
        p.join()  # this blocks until the process terminates
        exitcode = None
        while exitcode is None:  # make sure there is an exitcode
            exitcode = p.exitcode
        if exitcode != 0:
            raise Exception('processing failed')

    def run(self):  # pragma: no cover
        """
        run the daemon indefinitely
        """
        self.logger.info('daemon started')
        try:
            while True:
                self._subprocess_daemon()
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self._handle_manual_stop()
        except Exception as e:
            self._handle_unrecoverable_error(e)

    def _handle_manual_stop(self):
        self.logger.warn('manual stop')
        self.logger.warn('daemon stopped')

    def _handle_unrecoverable_error(self, ex):
        self.logger.error('unrecoverable error')
        self.logger.exception(ex)
        self.logger.warn('daemon stopped')
        raise ex
