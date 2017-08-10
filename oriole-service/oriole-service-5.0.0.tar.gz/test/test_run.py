from mock import patch
from pytest import *
from oriole_service.cli import setup_parser
from oriole_service.modules.run import main


@fixture
def p():
    return setup_parser()


def test_run(p):
    args = p.parse_args([
        'run',
        'log',
    ])

    with patch('oriole_service.api.run') as run:
        main(args)
        assert run.call_count == 1
        assert run.call_args[0][0] == 'log'


def test_r(p):
    args = p.parse_args([
        'r',
        'log',
    ])

    with patch('oriole_service.api.run') as run:
        main(args)
        assert run.call_count == 1
        assert run.call_args[0][0] == 'log'
