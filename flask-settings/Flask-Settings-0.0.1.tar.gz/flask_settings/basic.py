# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BasicConfig(object):
    DEBUG = False
    TESTING = False

    def __init__(self, app=None):
        super(BasicConfig, self).__init__()
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.settings = self
        app.config.from_object(self)
