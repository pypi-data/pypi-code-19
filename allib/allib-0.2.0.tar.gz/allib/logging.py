from __future__ import absolute_import
import logging
import logging.handlers
import sys

LOG = logging.getLogger(__name__)


def setup_logging(log_file=None, log_level=None, check_interactive=None):
	if log_level is None:
		log_level = logging.WARNING
	elif isinstance(log_level, str):
		log_level = getattr(logging, log_level.upper())
	root = logging.getLogger()
	root.setLevel(log_level)

	if not log_file or log_file.lower() == 'stderr':
		handler = logging.StreamHandler(sys.stderr)
		log_file = 'STDERR'
		check_interactive = False
	elif log_file.lower() == 'stdout':
		handler = logging.StreamHandler(sys.stdout)
		log_file = 'STDOUT'
		check_interactive = False
	elif log_file:
		handler = logging.handlers.WatchedFileHandler(log_file)
		if check_interactive is None:
			check_interactive = True

	# define the logging format
	logfmt = '%(asctime)s [%(levelname)8s] [%(name)s] %(message)s'
	formatter = logging.Formatter(logfmt)
	handler.setFormatter(formatter)

	# add the logging handler for all loggers
	root.addHandler(handler)

	LOG.info('set up logging to %s with level %s', log_file, log_level)

	# if logging to a file but the application is ran through an interactive
	# shell, also log to STDERR
	if check_interactive:
		if sys.__stderr__.isatty():
			console_handler = logging.StreamHandler(sys.stderr)
			console_handler.setFormatter(formatter)
			root.addHandler(console_handler)
			LOG.info('set up logging to STDERR with level %s', log_level)
		else:
			LOG.info('sys.stderr is not a TTY, not logging to it')
