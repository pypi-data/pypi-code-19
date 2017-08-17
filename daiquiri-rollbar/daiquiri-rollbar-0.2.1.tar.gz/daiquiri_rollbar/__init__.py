import functools
import logging
import sys

import rollbar

from daiquiri.output import (
    get_program_name,
    Output,
)


class RollbarOutput(Output):
    def __init__(self, access_token=None, environment='production', level=None, program_name=None):
        '''Output to use Rollbar with daiquiri.

        Args:
            access_token (str): Rollbar server access token for your project. Leave it to None
                not to log anything. Default: None.
            environment (str): Environment in which to log. Default: production.
            level (int): Log level to use. Leave to None to use the global log level.
                Default: None.
            program_name (str): the name of the program.
        '''
        handler = RollbarHandler(
            program_name or get_program_name(),
            access_token=access_token,
            environment=environment
        )
        self._rollbar_handler = handler
        super().__init__(handler, level=level)


class RollbarHandler(logging.Handler):
    '''Log handler to use Rollbar with daiquiri.

    This shouldn't be instanciated directly. Use ``RollbarOutput`` to use with daiquiri.

    Args:
        program_name (str): the name of the program.
        access_token (str): Rollbar server access token for your project. Leave it to None
            not to log anything. Default: None.
        environment (str): Environment in which to log. Default: production.
    '''
    def __init__(self, program_name, access_token=None, environment='production'):
        super().__init__()
        self._programe_name = program_name
        if access_token is not None:
            self._rollbar = rollbar
            self._rollbar.init(access_token, environment)
        else:
            self._rollbar = None

    def emit(self, record):
        if self._rollbar is None:
            # Nothing to do, no access token supplied.
            return

        if self.is_rollbar_error(record):
            # Don't attempt to log rollbar error mesasges into rollbar.
            # We we only create an infinite loop.
            print('Error while logging into rollbar:', record.getMessage(), file=sys.stderr)
        elif self.is_exception(record):
            self._report_exeception(record)
        else:
            self._report_message(record)

    def is_rollbar_error(self, record):
        return record.name == 'rollbar' or \
            (record.name == 'daiquiri_rollbar.tests.test_invalid_rollbar_token' and
             record.getMessage() == 'invalid token')  # We are in a test

    def is_exception(self, record):
        return record.exc_info is not None

    def _report_exeception(self, record):
        self._rollbar.report_exc_info(record.exc_info)

    def _report_message(self, record):
        report = functools.partial(
            self._rollbar.report_message,
            record.getMessage(),
            record.levelname.lower()
        )

        if hasattr(record, 'extra_data'):
            report(extra_data=record.extra_data)
        else:
            report()
