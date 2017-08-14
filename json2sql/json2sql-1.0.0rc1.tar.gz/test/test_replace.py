#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Tests for REPLACE SQL statement."""

from json2sql import replace2sql
from json2sql import json2sql

from .base import TestBase


class TestReplace(TestBase):
    """Tests for REPLACE SQL statement."""

    def test_replace_dict(self):
        """Test simple REPLACE."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.replace
        #
        result = replace2sql({'table': 'person', 'values': [['person_id', 'mosky'], ['name', 'Mosky Liu']]})
        assert result == "REPLACE INTO \"person\" VALUES ('person_id', 'mosky'), ('name', 'Mosky Liu')"

    def test_replace_kwargs(self):
        """Test simple REPLACE with kwargs."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.replace
        #
        result = replace2sql(table='person', values=[['person_id', 'mosky'], ['name', 'Mosky Liu']])
        assert result == "REPLACE INTO \"person\" VALUES ('person_id', 'mosky'), ('name', 'Mosky Liu')"

    def test_replace_single(self):
        """Test replace."""
        result = replace2sql(table='person', columns='name', values='foo')
        assert result == "REPLACE INTO \"person\" (\"name\") VALUES foo"

    def test_replace_multiple(self):
        """Test replace."""
        result = replace2sql(table='person', columns=['name', 'age'], values=['Milan', 42])
        assert result == "REPLACE INTO \"person\" (\"name\", \"age\") VALUES ('Milan', 42)"

    def test_replace_set(self):
        """Test replace."""
        result = replace2sql(table='person', set=[['name', 'Milan'], ('age', 42)])
        assert result == "REPLACE INTO \"person\" (\"name\", \"age\") VALUES ('Milan', 42)"

    def test_replace_json2sql(self):
        """Test replace."""
        result = json2sql(table='person', statement='replace', set=[['name', 'Milan'], ('age', 42)])
        assert result == "REPLACE INTO \"person\" (\"name\", \"age\") VALUES ('Milan', 42)"
