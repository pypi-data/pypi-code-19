#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Common tests across json2sql package."""

import os

import pytest
from json2sql import json2sql
from json2sql import UnknownStatementError
from json2sql import NoStatementError

from .base import TestBase


class TestCommon(TestBase):
    """Common tests across json2sql package."""

    _TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

    def test_empty(self):
        """Raise on empty input - data/empty.json."""
        empty_path = os.path.join(self._TEST_DATA_DIR, 'empty.json')

        with pytest.raises(UnknownStatementError):
            with open(empty_path, 'r') as f:
                json2sql(f)

    def test_input1_json(self):
        """Test parsing of data/input1.json."""
        input1_path = os.path.join(self._TEST_DATA_DIR, 'input1.json')
        # TODO: implement

    def test_input1_yaml(self):
        """Test parsing of data/input1.yaml."""
        input1_path = os.path.join(self._TEST_DATA_DIR, 'input1.yaml')
        # TODO: implement

    def test_input2_json(self):
        """Test parsing of data/input2.json."""
        input2_path = os.path.join(self._TEST_DATA_DIR, 'input2.json')
        # TODO: implement

    def test_input2_yaml(self):
        """Test parsing of data/input2.yaml."""
        input2_path = os.path.join(self._TEST_DATA_DIR, 'input2.yaml')
        # TODO: implement

    def test_no_statement(self):
        """Test no statement error."""
        with pytest.raises(NoStatementError):
            json2sql(table='person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu'))
