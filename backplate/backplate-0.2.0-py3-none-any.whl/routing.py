
def create_url(url):
    """Provide support for more concise route url definitions

    Convert '/entity/:id' into '/entity/<int:id>'
    Convert '/entity/string:id' into '/entity/<string:id>'
    """

    def select_type(_type):
        if _type == 'int':
            return 'int'
        elif _type == 'str':
            return 'string'
        else:
            return 'int'

    parts = url.split('/')
    parsed = []
    for part in parts:
        if part.find(':') != -1:
            child_type, name = part.split(':')
            child_type = select_type(child_type)
            parsed.append('<{}:{}>'.format(child_type, name))
        else:
            parsed.append(part)

    return '/{}'.format('/'.join(parsed))


class Route:
    def __init__(self,
                 name, url,
                 index_controller=None, child_controller=None,
                 children=[], child_type=int):

        self.name = name
        self.url = url
        self.index_controller = index_controller
        self.child_controller = child_controller
        self.children = children
        self.child_type = child_type


def create_routes(routes):
    """Returns an array of route tuples from a nested routes structure"""

    def select_type(_type):
        if _type is int:
            return 'int'
        elif _type is str:
            return 'str'
        else:
            return 'int'

    parsed = []

    def parse_routes(_routes, pre_url='', pre_end=''):
        """Recursive routes parsing function to generate endpoints"""

        for route in _routes:
            name = route.name
            url = route.url
            index_controller = route.index_controller
            child_controller = route.child_controller
            children = route.children
            child_type = route.child_type

            url = url[1:] if url.startswith('/') else url
            child_type = select_type(child_type)

            index_url = '{}/{}'.format(pre_url, url)
            child_url = '{}/{}/{}:{}_id'.format(pre_url, url, child_type, name)
            index_endpoint = '{}-{}-index'.format(pre_end, name)
            child_endpoint = '{}-{}-child'.format(pre_end, name)

            if index_url.startswith('/'):
                index_url = index_url[1:]
            if child_url.startswith('/'):
                child_url = child_url[1:]

            if index_endpoint.startswith('-'):
                index_endpoint = index_endpoint[1:]
            if child_endpoint.startswith('-'):
                child_endpoint = child_endpoint[1:]

            parsed.append((index_url, index_controller, index_endpoint))
            if child_controller:
                parsed.append((child_url, child_controller, child_endpoint))
                parse_routes(children, child_url, child_endpoint)
            else:
                index_endpoint = index_endpoint[:-len('-index')]
                parse_routes(children, index_url, index_endpoint)

    parse_routes(routes)
    return parsed


def bind_routes(api, routes=[]):
    """From an array of routes binds them to given restful_api object"""

    def add_route(url, controller, endpoint=None):
        if not controller:
            return
        url = create_url(url)
        api.add_resource(controller, url, endpoint=endpoint)

    for route in routes:
        url, controller, endpoint = route
        add_route(url, controller, endpoint)

__all__ = ['Route']
