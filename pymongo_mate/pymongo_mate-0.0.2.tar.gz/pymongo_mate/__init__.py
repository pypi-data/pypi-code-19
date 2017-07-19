#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.2"
__short_description__ = "A library extend pymongo module, makes CRUD easier."
__license__ = "MIT"

try:
    from .crud.insert import *
    from .crud.select import *
    from .crud.update import *
    from .query_builder import *
except:
    pass
