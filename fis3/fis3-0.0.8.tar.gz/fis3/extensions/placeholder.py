from jinja2 import nodes
from jinja2.ext import Extension
from ..resource import Resource


class FisPlaceholderExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['fis_placeholder'])

    def __init__(self, environment):
        super(FisPlaceholderExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]

        return nodes.CallBlock(self.call_method('_handler', args),
                               [], [], []).set_lineno(lineno)

    def _handler(self, hook_type, caller):
        """Helper callback."""
        return Resource.placeholder(hook_type)
