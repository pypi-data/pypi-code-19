#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `timee` package."""

import pytest
from click.testing import CliRunner
from freezegun import freeze_time
from timee import cli
from timee.timee_core import timee_parse, timee_parse_duration


@freeze_time("2017-02-15")
def test_timee_1():

    timee_dt = timee_parse('1 week ago')

    expected_basic_string = '2017-02-08 00:00:00'

    assert timee_dt.basic_string == expected_basic_string


# @freeze_time("2017-02-15")
# def test_timee_2():
#
#     timee_dt = timee_parse('30 days before Dec 1')
#
#     expected_basic_string = '2017-02-08 00:00:00'
#
#     assert timee_dt.basic_string == expected_basic_string


def test_timee_3():

    timee_duration = timee_parse_duration('30 days')

    expected_seconds = 2592000

    expected_string_conversion = '30 days'

    assert timee_duration.seconds == expected_seconds
    assert timee_duration.in_words == expected_string_conversion


@freeze_time("2017-08-13")
def test_timee_5():

    text = '08:00'

    timee_dt = timee_parse(text)

    assert timee_dt.basic_string == '2017-08-13 08:00:00'

    assert timee_dt.time == '08:00'


# @pytest.fixture
# def response():
#     """Sample pytest fixture.
#
#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'timee.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
