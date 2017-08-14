#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Tests for DELETE SQL statement."""

from json2sql import delete2sql
from json2sql import json2sql

from .base import TestBase


class TestDelete(TestBase):
    """Tests for DELETE SQL statement."""

    def test_delete_dict(self):
        """Test simple DELETE."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.delete
        #
        result = delete2sql({'table': 'person', 'where': {'person_id': 'mosky'}})
        assert result == "DELETE FROM \"person\" WHERE \"person_id\" = 'mosky'"

    def test_delete_kwargs(self):
        """Test simple DELETE with kwargs."""
        #
        # Taken from mosql:
        #   http://mosql.mosky.tw/query.html#mosql.query.delete
        #
        result = delete2sql(table='person', where={'person_id': 'mosky'})
        assert result == "DELETE FROM \"person\" WHERE \"person_id\" = 'mosky'"

    def test_delete_where(self):
        """Test DELETE WHERE."""
        result = delete2sql(table='person', where={'person_id': 'mosky'})
        assert result == "DELETE FROM \"person\" WHERE \"person_id\" = 'mosky'"

    def test_delete(self):
        """Test simple DELETE."""
        result = delete2sql(table='person')
        assert result == "DELETE FROM \"person\""

    def test_delete_returning(self):
        """Test DELETE RETURNING."""
        result = delete2sql(table='person', where={'person_id': 'mosky'}, returning='person_id')
        assert result == "DELETE FROM \"person\" WHERE \"person_id\" = 'mosky' RETURNING \"person_id\""

    def test_delete_returning_star(self):
        """Test DELETE RETURNING *."""
        result = delete2sql(table='person', where={'person_id': 'mosky'}, returning='*')
        assert result == "DELETE FROM \"person\" WHERE \"person_id\" = 'mosky' RETURNING *"

    def test_delete_json2sql(self):
        """Test DELETE using json2sql()."""
        result = json2sql({'table': 'person', 'statement': 'delete', 'where': {'person_id': 'mosky'}})
        assert result == "DELETE FROM \"person\" WHERE \"person_id\" = 'mosky'"
