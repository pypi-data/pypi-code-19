#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Tests for INSERT SQL statement."""

from json2sql import insert2sql
from json2sql import json2sql

from .base import TestBase


class TestInsert(TestBase):
    """Tests for INSERT SQL statement."""

    def test_insert_dict(self):
        """Test simple INSERT."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.insert
        #
        result = insert2sql({'table': 'person', 'values': [['person_id', 'mosky'], ['name', 'Mosky Liu']]})
        assert result == "INSERT INTO \"person\" VALUES ('person_id', 'mosky'), ('name', 'Mosky Liu')"

    def test_insert_kwargs(self):
        """Test simple INSERT with kwargs."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.insert
        #
        result = insert2sql(table='person', values=[['person_id', 'mosky'], ['name', 'Mosky Liu']])
        assert result == "INSERT INTO \"person\" VALUES ('person_id', 'mosky'), ('name', 'Mosky Liu')"

    def test_insert_set(self):
        """Test INSERT with a simple set."""
        result = insert2sql(table='person', set=[('person_id', 'mosky'), ('name', 'Mosky Liu')])
        assert result == "INSERT INTO \"person\" (\"person_id\", \"name\") VALUES ('mosky', 'Mosky Liu')"

    def test_insert_duplicate_key(self):
        """Test INSERT with duplicate key check."""
        result = insert2sql(table='person', values=('mosky', 'Mosky Liu'),
                            on_duplicate_key_update={'name': 'Mosky Liu'}, returning='person_id')
        assert result == "INSERT INTO \"person\" VALUES ('mosky', 'Mosky Liu') " \
                         "RETURNING \"person_id\" ON DUPLICATE KEY UPDATE \"name\"='Mosky Liu'"

    def test_insert_returning_star(self):
        """Test INSERT RETURNING *."""
        result = insert2sql(table='person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu'), returning="*")
        assert result == "INSERT INTO \"person\" (\"person_id\", \"name\") VALUES (\'mosky\', \'Mosky Liu\') " \
                         "RETURNING *"

    def test_insert_returning(self):
        """Test INSERT RETURNING."""
        result = insert2sql(table='person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu'),
                            returning="person_id")
        assert result == "INSERT INTO \"person\" (\"person_id\", \"name\") VALUES (\'mosky\', \'Mosky Liu\') " \
                         "RETURNING \"person_id\""

    def test_insert_json2sql(self):
        """Test INSERT RETURNING."""
        result = json2sql(table='person', statement='insert', columns=('person_id', 'name'),
                          values=('mosky', 'Mosky Liu'))
        assert result == "INSERT INTO \"person\" (\"person_id\", \"name\") VALUES (\'mosky\', \'Mosky Liu\')"
