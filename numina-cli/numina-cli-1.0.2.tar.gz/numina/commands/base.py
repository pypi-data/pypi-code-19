"""The base command."""


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.request_url = 'https://api.numina.co'
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('Not implemented')
