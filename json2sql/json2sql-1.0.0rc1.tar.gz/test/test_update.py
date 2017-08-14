#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Tests for UPDATE SQL statement."""

from json2sql import update2sql
from json2sql import json2sql

from .base import TestBase


class TestUpdate(TestBase):
    """Tests for UPDATE SQL statement."""

    def test_update_dict(self):
        """Test simple UPDATE."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.update
        #
        result = update2sql({'table': 'person', 'where': {'person_id': 'mosky'}, 'set': {'name': 'Mosky Liu'}})
        assert result == 'UPDATE "person" SET "name"=\'Mosky Liu\' WHERE "person_id" = \'mosky\''

    def test_update_kwargs(self):
        """Test simple UPDATE with kwargs."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.update
        #
        result = update2sql(table='person', where={'person_id': 'mosky'}, set={'name': 'Mosky Liu'})
        assert result == 'UPDATE "person" SET "name"=\'Mosky Liu\' WHERE "person_id" = \'mosky\''

    def test_update_set_only(self):
        """Test UPDATE with SET only."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.update
        #
        result = update2sql({'table': 'person', 'set': {'name': 'Mosky Liu'}})
        assert result == 'UPDATE "person" SET "name"=\'Mosky Liu\''

    def test_update_where_only(self):
        """Test UPDATE without SET."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.update
        #
        result = update2sql({'table': 'person', 'where': {'name': 'Mosky Liu'}})
        assert result == 'UPDATE "person" WHERE "name" = \'Mosky Liu\''

    def test_update_returning_star(self):
        """Test UPDATE with RETURNING *."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.update
        #
        result = update2sql({'table': 'person',
                             'set': {'person_id': 'mosky'},
                             'where': {'name': 'Mosky Liu'},
                             'returning': '*'})
        assert result == 'UPDATE "person" SET "person_id"=\'mosky\' WHERE "name" = \'Mosky Liu\' RETURNING *'

    def test_update_returning(self):
        """Test UPDATE with RETURNING."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.update
        #
        result = update2sql({'table': 'person',
                             'set': {'person_id': 'mosky'},
                             'where': {'name': 'Mosky Liu'},
                             'returning': 'person_id'})
        assert result == 'UPDATE "person" SET "person_id"=\'mosky\' WHERE "name" = \'Mosky Liu\' RETURNING "person_id"'

    def test_update_kwargs(self):
        """Test UPDATE using json2sql."""
        result = json2sql(table='person', statement='update', where={'person_id': 'mosky'}, set={'name': 'Mosky Liu'})
        assert result == 'UPDATE "person" SET "name"=\'Mosky Liu\' WHERE "person_id" = \'mosky\''

