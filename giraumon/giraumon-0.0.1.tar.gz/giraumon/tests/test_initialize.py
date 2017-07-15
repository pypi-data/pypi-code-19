# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from click.testing import CliRunner
from giraumon.initialize import init


def test_init_without_git_repo():
    """Test init on folder with no git root """
    runner = CliRunner()
    result = runner.invoke(init, ['/tmp'])
    assert result.exit_code == 1
    assert 'Not a valid repository' in result.output


def test_init_without_git_force_repo():
    """Test init on folder with no git root and force option"""
    runner = CliRunner()
    result = runner.invoke(init, ['/tmp', '--force'])
    assert result.exit_code == 0
    assert 'Initialise Hosting Configuration in' in result.output


def test_init_with_git_repo():
    """Test init on folder with git root """
    runner = CliRunner()
    result = runner.invoke(init, ['.'])
    assert result.exit_code == 0
    assert 'Initialise Hosting Configuration in' in result.output
