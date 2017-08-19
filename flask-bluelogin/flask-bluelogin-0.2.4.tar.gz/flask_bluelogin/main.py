#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join, dirname
import uuid
from flask_login import LoginManager

from flask import Blueprint, current_app, send_from_directory, redirect, request, send_file
from .controllers.login_controller import login, logout, add_user, get_user, set_user
from .util import check_login
from .models.users import Users

def static_web_index():
    return send_from_directory(join(dirname(__file__),'swagger-ui'),"index.html")

def static_web(filename):
    if filename == "index.html":
        return redirect(request.url[:-1 * len('index.html')])
    if filename == "swagger.yaml":
        swagger = open(join(dirname(__file__),'swagger-ui','swagger.yaml'),'r').read()
        swagger = swagger.replace('$host$', "%s:%s" % (request.environ['SERVER_NAME'], request.environ['SERVER_PORT']) )
        swagger = swagger.replace('$path$', [current_app.blueprints[i] for i in current_app.blueprints if current_app.blueprints[i].__class__.__name__ == 'BlueLogin'][0].url_prefix )
        return swagger
    return send_from_directory(join(dirname(__file__),'swagger-ui'),filename)

class BlueLogin(Blueprint):

    def __init__(self, name='bluelogin', import_name=__name__, ui_testing=False, url_prefix="", group_name='admin', *args, **kwargs):
        Blueprint.__init__(self, name, import_name, url_prefix=url_prefix, *args, **kwargs)
        self._add_check_login_list = []
        self._grp = group_name
        self._add_url_rule(ui_testing)
        self.before_app_first_request(self._init_login_manager)
    
    def _init_login_manager(self):
        self._login_manager = LoginManager()
        self._login_manager.init_app(current_app)
        if not current_app.secret_key:
            current_app.secret_key = str(uuid.uuid4())
            current_app.logger.warning("not secret key for app, generate secret key")

        @self._login_manager.user_loader
        def load_user(id):
            return Users().get_user(id)
       
        for i in self._add_check_login_list:
            if i[1]:
                 current_app.view_functions[i[0]] = check_login(*i[1])(current_app.view_functions[i[0]])
            else:
                current_app.view_functions[i[0]] = check_login()(current_app.view_functions[i[0]])
        current_app.logger.debug("add login manager")
    
    def _add_url_rule(self, ui_testing=False):
        self.add_url_rule('/logout', 'logout', logout, methods=['GET'])
        self.add_check_login("%s.logout" % self.name)
        self.add_url_rule('/login', 'login', login, methods=['PUT'])
        self.add_url_rule('/user', 'add_user', add_user, methods=['PUT'])
        self.add_check_login("%s.add_user" % self.name, self._grp)
        self.add_url_rule('/user/<userId>', 'get_user', get_user, methods=['GET'])
        self.add_check_login("%s.get_user" % self.name)
        self.add_url_rule('/user/<userId>', 'set_user', set_user, methods=['PUT'])
        self.add_check_login("%s.set_user" % self.name, self._grp)
        if ui_testing:
            self.add_url_rule('/login/ui/<path:filename>', 'static_web', static_web)
            self.add_url_rule('/login/ui/', 'static_web_index', static_web_index)
    
    def _add_check_login(self, endpoint, *groups):
        try:
            current_app.view_functions[endpoint] = check_login(*groups)(current_app.view_functions[endpoint])
        except RuntimeError as e:
            self._add_check_login_list.append([endpoint, groups])

    def add_check_login(self, endpoints, *groups):
        if isinstance(endpoints, list):
            for endpoint in endpoints:
                self._add_check_login(endpoint, *groups)
        else:
            self._add_check_login(endpoints, *groups)
