import logging

import daiquiri

from .. import RollbarOutput


def test_no_access_token():
    rollbar_output = RollbarOutput()
    daiquiri.setup(
        level=logging.INFO,
        outputs=(rollbar_output,)
    )
    logger = daiquiri.getLogger(__name__)

    logger.info('test')

    assert rollbar_output._rollbar_handler._rollbar is None


def test_invalid_token(capsys):
    rollbar_output = RollbarOutput(access_token='invalid')
    daiquiri.setup(
        level=logging.INFO,
        outputs=(rollbar_output,)
    )
    logger = daiquiri.getLogger(__name__)
    rollbar_called = []

    def call_rollbar(message, levelname):
        rollbar_called.append(True)
        assert levelname == 'info'
        assert message == 'test'

        logger.exception('invalid token')

    rollbar_output._rollbar_handler._rollbar.report_message = call_rollbar

    logger.info('test')

    out, err = capsys.readouterr()
    assert len(rollbar_called) == 1
    assert rollbar_called[0]
    assert err == 'Error while logging into rollbar: invalid token\n'
