import pytest
from click.testing import CliRunner
from awsparams import awsparams


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture(scope="function")
def new_param(cli_runner):
    yield cli_runner.invoke(awsparams.new, ['--name', 'testing.testing.testing', '--value', '1234', '--param_type', 'SecureString'])
    cli_runner.invoke(awsparams.rm, ['testing.testing.testing', '-f'])


def test_new(cli_runner, new_param):
    result = new_param
    assert result.exit_code == 0
    assert result.output.strip() == ''


def test_new_simple(cli_runner):
    result = cli_runner.invoke(awsparams.new, ['--name', 'testing.testing.testing', '--value', '1234'])
    assert result.exit_code == 0
    cli_runner.invoke(awsparams.rm, ['testing.testing.testing', '-f'])


def test_version():
    assert awsparams.__VERSION__ == '0.9.3'


def test_connect_ssm():
    assert awsparams.connect_ssm()


def test_translate_results():
    parms = [{'Name': 'test', 'Description': 'testing'}]
    assert awsparams.translate_results(parms) == ['test']


def test_ls(cli_runner, new_param):
    result = cli_runner.invoke(awsparams.ls, ['testing.testing.'])
    assert result.exit_code == 0
    assert result.output.strip() == "testing.testing.testing"


def test_ls_values(cli_runner, new_param):
    result = cli_runner.invoke(awsparams.ls, ['testing.testing.', '-v', '--with-decryption'])
    assert result.exit_code == 0
    assert result.output.strip() == "testing.testing.testing: 1234"


def test_cp_basic(cli_runner, new_param):
    result = cli_runner.invoke(awsparams.cp, ['testing.testing.testing', 'testing.testing.newthing'])
    assert result.exit_code == 0
    assert result.output.strip() == 'Copied testing.testing.testing to testing.testing.newthing'
    cli_runner.invoke(awsparams.rm, ['testing.testing.newthing', '-f'])


def test_cp_fail(cli_runner):
    result = cli_runner.invoke(awsparams.cp, ['testing.testing.testing'])
    assert result.exit_code == 0
    assert result.output.strip() == 'dst (Destination) is required when not copying to another profile'


def test_rm(cli_runner):
    cli_runner.invoke(awsparams.new, ['--name', 'testing.testing.testing', '--value', '1234'])
    result = cli_runner.invoke(awsparams.rm, ['testing.testing.testing', '-f'])
    assert result.exit_code == 0
