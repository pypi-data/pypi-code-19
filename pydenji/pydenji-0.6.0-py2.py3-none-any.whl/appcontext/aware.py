#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from abc import abstractmethod
from pydenji.ducktypes.ducktype import DuckABCMeta

class AppContextAware(object):
    __metaclass__ = DuckABCMeta

    @abstractmethod
    def set_app_context(self, context):
        pass

