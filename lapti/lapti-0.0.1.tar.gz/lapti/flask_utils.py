# -*- coding: utf-8 -*-
import json
import math
from inspect import isclass

from flask import request, redirect, render_template, make_response, url_for, current_app
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_admin.contrib.peewee.form import CustomModelConverter
from flask_admin.contrib.peewee import ModelView
from playhouse.fields import CompressedField
from wtforms import fields, TextAreaField

from lapti.peewee_utils import JSONField, CompressedJSONField


__all__ = [
    'ProtectedModelView', 'ProtectedModelViewRO', 'DeveloperModelView', 'DeveloperModelViewRO',
    'do_redirect', 'register', 'Handler',
    'HandlerException', 'TemplateError', 'DeniedException', 'FormException', 'HandlerRedirect',
    'Pagination',
    'ActionManager', 'APIHandler', 'LoggedInAPIHandler', 'ActionAPI', 'LoggedInActionAPI'
]


class CustomModelAdminConverter(CustomModelConverter):
    def __init__(self, view, additional=None):
        super(CustomModelAdminConverter, self).__init__(additional)

        self.converters[JSONField] = self.handle_json
        self.converters[CompressedField] = self.handle_text
        self.converters[CompressedJSONField] = self.handle_json

    def handle_json(self, model, field, **kwargs):
        return field.name, DictToJSONField(**kwargs)

    def handle_text(self, model, field, **kwagrs):
        return field.name, fields.TextAreaField(**kwagrs)


class DictToJSONField(TextAreaField):
    def process_data(self, value):
        if value is None:
            value = {}

        self.data = json.dumps(value, indent=2, ensure_ascii=False)

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = json.loads(valuelist[0])


class ProtectedModelView(ModelView):
    model_form_converter = CustomModelAdminConverter

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class ProtectedModelViewRO(ProtectedModelView):
    action_disallowed_list = ('edit', 'delete', 'create')
    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = True


class DeveloperModelView(ProtectedModelView):
    def is_accessible(self):
        return super(DeveloperModelView, self).is_accessible() and current_user.is_developer


class DeveloperModelViewRO(ProtectedModelViewRO):
    def is_accessible(self):
        return super(DeveloperModelViewRO, self).is_accessible() and current_user.is_developer


def register(app):
    def decorator(cls):
        for route in cls.routes:
            if not isinstance(route, dict):
                route = {'rule': route}
            if 'endpoint' not in route:
                route['endpoint'] = cls.__name__.lower()

            route['view_func'] = cls.as_view(route['endpoint'])

            if 'methods' not in route:
                route['methods'] = ['GET']

            app.add_url_rule(**route)
        return cls
    return decorator


def do_redirect(location):
    raise HandlerRedirect(location)


class HandlerException(Exception):
    pass


class TemplateError(Exception):
    pass


class DeniedException(TemplateError):
    pass


class FormException(TemplateError):
    pass


class HandlerRedirect(Exception):
    def __init__(self, redirect=None, *args, **kwargs):
        self.redirect = redirect
        super(HandlerRedirect, self).__init__(*args, **kwargs)


class Handler(MethodView):
    routes = [
        # Стандартные аргументы app.route. endpoint обязателен
        # {
        #     'rule': '/',
        #     'endpoint': 'index',
        #     'methods': ['GET']
        # }
    ]
    template = ''
    form_error_template = 'errors/form.html'
    denied_error_template = 'errors/denied.html'
    error_template = 'errors/error.html'
    method_decorators = {
        # Декораторы только для конкретных методов
        # 'post': [login_required]
    }

    def __init__(self, *args, **kwargs):
        self.cookies = []
        self.args = ()
        self.kwargs = {}
        self.request = None
        super(Handler, self).__init__()

    def get_context_data(self, *args, **kwargs):
        return {}

    def bind_cookies(self, resp):
        for cookie, val in self.cookies:
            if not isinstance(val, dict):
                val = {'value': val}
            resp.set_cookie(cookie, **val)
        return resp

    def set_cookie(self, name, val):
        self.cookies.append((name, val))

    def response(self, *args, **kwargs):
        if not self.template:
            raise HandlerException('No template specified')

        return self.render_template(self.template, **self.get_context_data(*args, **kwargs))

    def render_template(self, template, **kwargs):
        login_next = request.args.get('next') or request.form.get('next') or request.url
        return render_template(template, login_next=login_next, current_user=current_user, **kwargs)

    def get(self, *args, **kwargs):
        return self.response(*args, **kwargs)

    def post(self, *args, **kwargs):
        assert None is not None, 'Unimplemented method %r' % request.method

    def template_error_response(self, e, template):
        return self.bind_cookies(make_response(render_template(template, message=str(e))))

    @staticmethod
    def redirect(endpoint=None, url=None, **kwargs):
        raise HandlerRedirect(url_for(endpoint, **kwargs) if url is None else url)

    def dispatch_request(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = request

        additional_decorators = self.method_decorators.get(str(request.method).lower())
        view = super(Handler, self).dispatch_request
        if additional_decorators is not None:
            for decorator in additional_decorators:
                view = decorator(view)

        try:
            return self.bind_cookies(make_response(view(*args, **kwargs)))
        except HandlerRedirect as e:
            return self.bind_cookies(redirect(e.redirect))
        except FormException as e:
            return self.template_error_response(e, self.form_error_template)
        except DeniedException as e:
            return self.template_error_response(e, self.denied_error_template)
        except TemplateError as e:
            return self.template_error_response(e, self.error_template)


class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(math.ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def need_first(self):
        return self.page > 10

    @property
    def need_last(self):
        return self.page < (self.pages - 10)

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                self.page - left_current - 1 < num < self.page + right_current
            ) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class _APIStatusMixin(object):
    class BadData(Exception):
        pass

    @classmethod
    def good(cls, **kwargs):
        return dict(success=True, **kwargs)

    @classmethod
    def bad(cls, message=None, **kwargs):
        return dict(success=False, message=message, **kwargs)


class APIHandler(Handler, _APIStatusMixin):
    def __init__(self, *args, **kwargs):
        self.log = current_app.logger
        super(APIHandler, self).__init__(*args, **kwargs)

    @classmethod
    def response_json(cls, res):
        return current_app.response_class(
            json.dumps(res, indent=None if request.is_xhr else 2, ensure_ascii=True),
            mimetype='application/json'
        )


class LoggedInAPIHandler(APIHandler):
    decorators = [login_required]


class ActionManager(_APIStatusMixin):
    def __init__(self):
        self.log = current_app.logger

    def act(self, action):
        action_method = getattr(self, 'act_{}'.format(action), None)
        if action_method is None or not callable(action_method):
            return self.bad(_('Unknown API action: {}').format(action))

        return action_method()


class ActionAPI(APIHandler):
    def dispatch_request(self, *args, **kwargs):
        if request.method != 'POST':
            return self.response_json(self.bad('Invalid HTTP method'))
        api_method = request.form.get('type') or ''
        api_method = api_method.split('/', 1)
        if len(api_method) == 1:
            api_method = api_method[0]
            action = None
        else:
            api_method, action = api_method
        cls_name = 'do_{}'.format(api_method)
        cls = getattr(self, cls_name, None)
        if cls is not None and isclass(cls) and issubclass(cls, ActionManager):
            try:
                res = cls().act(action)
            except Exception as e:
                self.log.exception(e)
                res = self.bad(_('Exception on {}').format(action))
        else:
            res = self.bad(_('Unknown API method: {}.').format(api_method))
        if isinstance(res, (dict, list)):
            return self.response_json(res)
        return res


class LoggedInActionAPI(ActionAPI):
    decorators = [login_required]
