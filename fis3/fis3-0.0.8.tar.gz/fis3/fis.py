#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import sys
from resource import Resource
import extensions


class FIS:

    def __init__(self, app, **args):
        self.__add_extension(app)
        Resource.set_config(**args)

    @classmethod
    def render_template(cls, res_id, **context):
        return Resource.render_template(res_id, **context)

    @classmethod
    def __add_extension(cls, app):
        cls = inspect.getmembers(sys.modules[extensions.__name__], inspect.isclass)
        for ext in cls:
            app.jinja_env.add_extension(ext[1])

