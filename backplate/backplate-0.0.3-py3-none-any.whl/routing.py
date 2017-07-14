
def create_url(url):
    """Provide support for more concise route url definitions

    Convert '/entity/:id' into '/entity/<int:id>'
    Convert '/entity/string:id' into '/entity/<string:id>'
    """

    parts = url.split('/')
    parsed = []
    for part in parts:
        if part.find(':') != -1:
            kind, name = part.split(':')
            parsed.append('<{}:{}>'.format(kind or 'int', name))
        else:
            parsed.append(part)

    return '/{}'.format('/'.join(parsed))


def create_endpoint(url):
    """Provide support for using route urls to generate endpoint definitions

    Convert '/entity' into 'entity-index'
    Convert '/entity/:id' into 'entity-child'
    Convert '/entity/:id/subent' into 'entity-child-subent-index'
    Convert '/entity/:id/subent/:id' into 'entity-child-subent-child'
    """

    parts = url.split('/')
    parsed = []
    for part in parts:
        if part.find(':') != -1:
            parsed.append('child')
        else:
            parsed.append(part)

    if parsed[-1] != 'child':
        parsed.append('index')

    return '-'.join(parsed)


def endpoint(name, url,
             index_controller=None, child_controller=None,
             children=[], child_type='int'):
    """Returns a tuple to contruct API routes"""
    return (name, url, index_controller, child_controller, children, child_type)


def create_routes(routes):
    """Returns an array of route tuples from a nested routes structure"""

    parsed = []

    def parse_routes(_routes, pre_url='', pre_end=''):
        """Recursive routes parsing function to generate endpoints"""

        for route in _routes:
            name, url, index_controller, child_controller, children, child_type = route # noqa

            url = url[1:] if url.startswith('/') else url

            index_url = '{}/{}'.format(pre_url, url)
            child_url = '{}/{}/{}:id'.format(pre_url, url, child_type)
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
            if not child_controller:
                index_endpoint = index_endpoint[:-len('-index')]

            parsed.append((index_url, index_controller, index_endpoint))
            if child_controller:
                parsed.append((child_url, child_controller, child_endpoint))
                parse_routes(children, child_url, child_endpoint)
            else:
                parse_routes(children, index_url, index_endpoint)

    parse_routes(routes)
    return parsed


def add_endpoint(api, url, controller, endpoint=None):
    """Adds an endpoint to given restful_api object"""

    url = create_url(url)
    if not endpoint:
        endpoint = create_endpoint(url)

    return api.add_resource(controller, url, endpoint=endpoint)


def bind_routes(api, routes=[]):
    """From an array of routes binds them to given restful_api object"""

    for route in routes:
        url, controller, endpoint = route
        add_endpoint(api, url, controller, endpoint)

__all__ = ['endpoint']
