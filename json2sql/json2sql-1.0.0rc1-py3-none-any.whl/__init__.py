#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Convert JSON to raw SQL statement."""

from .errors import ClauseError
from .errors import InputError
from .errors import Json2SqlError
from .errors import Json2SqlInternalError
from .errors import NoStatementError
from .errors import ParsingInputError
from .errors import UnknownStatementError
from .json2sql import delete2sql
from .json2sql import insert2sql
from .json2sql import json2sql
from .json2sql import replace2sql
from .json2sql import select2sql
from .json2sql import update2sql

__version__ = '1.0.0rc1'
__version_info__ = __version__.split('.')
__title__ = 'json2sql'
__author__ = 'Fridolin Pokorny'
__license__ = 'ASL 2.0'
__copyright__ = 'Copyright 2017 Fridolin Pokorny'
