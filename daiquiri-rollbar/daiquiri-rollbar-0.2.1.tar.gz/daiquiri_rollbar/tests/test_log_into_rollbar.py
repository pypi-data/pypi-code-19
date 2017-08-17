import logging

from unittest.mock import MagicMock

import daiquiri
import pytest

from .. import (
    RollbarHandler,
    RollbarOutput,
)


@pytest.fixture(scope='function')
def rollbar_output(mock):
    rollbar = MagicMock()
    mock.patch('daiquiri_rollbar.rollbar', return_value=rollbar)

    rollbar_output = RollbarOutput(access_token='access_token')
    rollbar_output._rollbar_handler._rollbar = MagicMock()

    return rollbar_output


@pytest.fixture
def logger(rollbar_output):
    daiquiri.setup(
        level=logging.WARNING,
        outputs=(rollbar_output,)
    )

    return daiquiri.getLogger(__name__)


def test_init_rollbar_default_env(mock):
    rollbar = MagicMock()
    mock.patch('daiquiri_rollbar.rollbar', return_value=rollbar)

    handler = RollbarHandler('prog name', 'access_token')

    handler._rollbar.init.assert_called_once_with('access_token', 'production')


def test_init_rollbar_env(mock):
    rollbar = MagicMock()
    mock.patch('daiquiri_rollbar.rollbar', return_value=rollbar)

    handler = RollbarHandler('prog name', 'access_token', 'development')

    handler._rollbar.init.assert_called_once_with('access_token', 'development')


def test_basic_log(rollbar_output, logger):
    logger.warning('test')

    rollbar = rollbar_output._rollbar_handler._rollbar
    rollbar.report_message.assert_called_once_with('test', 'warning')


def test_log_with_extra_data(rollbar_output, logger):
    logger.warning('test', extra_data={'tester': 'pytest'})

    rollbar = rollbar_output._rollbar_handler._rollbar
    rollbar.report_message.assert_called_once_with(
        'test',
        'warning',
        extra_data={'tester': 'pytest'}
    )


def test_log_lower_level_than_what_we_must_record(rollbar_output, logger):
    try:
        raise Exception('An error occured')
    except Exception:
        logger.exception('oops')

    rollbar = rollbar_output._rollbar_handler._rollbar
    assert rollbar.report_exc_info.called == 1
    call_args = rollbar.report_exc_info.call_args[0][0]

    assert call_args[0] == Exception
    assert call_args[1].args == ('An error occured',)
