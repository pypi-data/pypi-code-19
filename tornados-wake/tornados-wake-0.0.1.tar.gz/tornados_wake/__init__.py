import inspect
import json
from operator import itemgetter

from tornado.web import RequestHandler


def get_routes_list(application, excludes=frozenset()):
    return sorted(((i._path, _methods_from_handler_class(i.handler_class))
                   for i in application.handlers[0][1]
                   if i._path and i._path not in excludes),
                  key=itemgetter(0))


def get_route_tree_dict(routes_list, include_methods=True):
    d = {}
    for route, methods in routes_list:
        route_split = route.split('/')[1:]  # eliminate empty string in leading position
        subdict = d
        for depth, segment in enumerate(route_split):
            if '/' + segment not in subdict:
                is_last_segment = depth == len(route_split) - 1
                subdict['/' + segment] = {'': methods if include_methods else None} if is_last_segment else {}
            subdict = subdict['/' + segment]
    return d


def make_route_handler(base_handler=RequestHandler,
                       excludes=frozenset(),
                       tree_keyword='tree', tree_default=False,
                       methods_keyword='methods', methods_default=True,
                       jsonify=True, respond_func_str='finish'):

    class RouteHandler(base_handler):

        def get(self):
            include_methods = methods_keyword and arg_bool(self.get_argument(methods_keyword, methods_default))
            make_tree = tree_keyword and arg_bool(self.get_argument(tree_keyword, tree_default))

            routes = get_routes_list(self.application, excludes=excludes)

            if make_tree:
                payload = {'routes': get_route_tree_dict(routes, include_methods=include_methods)}
            elif include_methods:
                payload = {'routes': routes}
            else:
                payload = {'routes': [r[0] for r in routes]}
            respond_func = getattr(self, respond_func_str)

            respond_func(json.dumps(payload, sort_keys=True) if jsonify else payload)

    return RouteHandler


def arg_bool(val_string):
    try:
        return bool(json.loads(val_string.lower()))
    except:
        return bool(val_string)


def _methods_from_handler_class(hc):
    """
    Given a handler class, return supported methods.
    Will *not* work for any methods set dynamically (like setattr in the `prepare` or something)

    :param hc: Handler class
    :return: list of implemented methods ex. ['GET', 'POST' 'PUT']
    """

    EXCLUDED_BASES = {RequestHandler, object}
    mro_classes = inspect.getmro(hc)
    mro_classes_filtered = [c for c in mro_classes if c not in EXCLUDED_BASES]

    candidates = hc.SUPPORTED_METHODS
    result = []
    for candidate in candidates:
        if any((candidate.lower() in klass.__dict__) for klass in mro_classes_filtered):
            result.append(candidate)
    return result


### Flask bonus

def get_flask_routes():
    from flask import current_app
    return [(r.rule, r.methods) for r in current_app.url_map.iter_rules()]
