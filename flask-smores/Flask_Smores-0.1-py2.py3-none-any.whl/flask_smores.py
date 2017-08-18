from flask import jsonify, request, current_app
from functools import wraps


# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Smores(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('CACHE_API_DOCS', True)
        app.config.setdefault('API_DOCS_RULE', '/api_docs')

        if app.config.get('CACHE_API_DOCS'):
            def api_docs():
                api_docs = getattr(app, '_api_docs', {})
                return jsonify(api_docs)

            app.add_url_rule(app.config['API_DOCS_RULE'], 'api_docs', api_docs)

            @app.before_first_request
            def cache_api_docs():
                app._api_docs = {}
                possible_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                for rule in app.url_map.iter_rules():
                    view_func = app.view_functions[rule.endpoint]
                    if getattr(view_func, '_uses_smores', False):
                        methods = [x for x in possible_methods if x in rule.methods]
                        doc_dict = {}
                        if view_func.__doc__:
                            doc_dict['description'] = view_func.__doc__
                        if getattr(view_func, '_input_schema'):
                            doc_dict['inputs'] = schema_dict(view_func._input_schema)
                        if getattr(view_func, '_output_schema'):
                            doc_dict['outputs'] = schema_dict(view_func._output_schema)
                        for method in methods:
                            try:
                                app._api_docs[rule.rule][method] = doc_dict
                            except KeyError:
                                app._api_docs[rule.rule] = {method: doc_dict}


REQUEST_ATTR_MAP = {
    'path': 'view_args',
    'query': 'args',
    'header': 'headers',
    'cookie': 'cookies'
}


def schema_dict(schema):
    schema_dict = {}
    for field_name, field in schema.fields.items():
        field_dict = {
            'default': field.default if field.default else None,
            'required': field.required if field.required else False,
            'type': field.__class__.__name__
        }
        field_dict.update(field.metadata)
        schema_dict[field_name] = field_dict
    return schema_dict


def use_input_schema(schema):
    def view_decorator(func):
        func._uses_smores = True
        func._input_schema = schema
        found_ins = {}
        for field_name, field in schema.fields.items():
            if field.metadata.get('found_in') in {'path', 'query', 'header', 'cookie', 'json'}:
                found_ins[field_name] = field.metadata['found_in']

        @wraps(func)
        def decorated_view(*args, **kwargs):
            data = {}
            data.update(request.headers)
            data.update(request.cookies)
            data.update(request.args)
            data.update(request.view_args)
            json = request.get_json()
            try:
                data.update(json)
            except TypeError:
                pass

            for field_name, found_in in found_ins.items():
                if found_in == 'json':
                    try:
                        data[field_name] = json.get(field_name)
                    except AttributeError:
                        pass
                else:
                    try:
                        data[field_name] = getattr(request, REQUEST_ATTR_MAP[found_in]).get(field_name)
                    except AttributeError:
                        pass

            result = schema.load(data=data)
            if result.errors:
                return jsonify(errors=result.errors), 400
            # validate and return 400 if invalid
            request.input_obj = result.data
            try:
                return func(input_obj=result.data, *args, **kwargs)
            except TypeError:
                return func(*args, **kwargs)

        return decorated_view

    return view_decorator


def use_output_schema(schema):
    def view_decorator(func):
        func._uses_smores = True
        func._output_schema = schema
        return func
    return view_decorator
